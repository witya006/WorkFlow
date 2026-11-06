#include "client455_network_codec.h"
#include "client455_network_defaults.h"
#include <cstring>

namespace {
std::uint8_t multiply(std::uint8_t a, std::uint8_t b) {
    std::uint8_t result = 0;
    while (b) {
        if (b & 1) result ^= a;
        a = static_cast<std::uint8_t>((a << 1) ^ ((a & 128) ? 0x11b : 0));
        b >>= 1;
    }
    return result;
}
std::uint8_t rotate(std::uint8_t value, unsigned bits) {
    return static_cast<std::uint8_t>((value << bits) | (value >> (8-bits)));
}
struct Substitution {
    std::uint8_t forward[256], inverse[256];
    Substitution() {
        for (unsigned i=0; i<256; ++i) {
            std::uint8_t a=static_cast<std::uint8_t>(i), reciprocal=1, power=a;
            for (unsigned exponent=254; exponent; exponent>>=1) {
                if (exponent & 1) reciprocal=multiply(reciprocal,power);
                power=multiply(power,power);
            }
            if (!i) reciprocal=0;
            const std::uint8_t value=reciprocal ^ rotate(reciprocal,1) ^ rotate(reciprocal,2)
                ^ rotate(reciprocal,3) ^ rotate(reciprocal,4) ^ 0x63;
            forward[i]=value; inverse[value]=static_cast<std::uint8_t>(i);
        }
    }
};
const Substitution& substitution() { static const Substitution table; return table; }
void addKey(std::uint8_t* state,const std::uint8_t* key) {
    for (unsigned i=0;i<16;++i) state[i]^=key[i];
}
void shift(std::uint8_t* state,bool inverse) {
    std::uint8_t original[16];std::memcpy(original,state,16);
    for(unsigned column=0;column<4;++column)for(unsigned row=0;row<4;++row)
        state[4*column+row]=original[4*((column+(inverse?4-row:row))%4)+row];
}
void mix(std::uint8_t* state,bool inverse) {
    for(unsigned column=0;column<4;++column) {
        std::uint8_t a[4];std::memcpy(a,state+4*column,4);
        for(unsigned row=0;row<4;++row) {
            const std::uint8_t* coefficients=inverse?
                reinterpret_cast<const std::uint8_t*>("\x0e\x0b\x0d\x09"):
                reinterpret_cast<const std::uint8_t*>("\x02\x03\x01\x01");
            state[4*column+row]=0;
            for(unsigned i=0;i<4;++i) state[4*column+row]^=multiply(a[(row+i)%4],coefficients[i]);
        }
    }
}
std::uint16_t word(const std::uint8_t* p) { return p[0] | (static_cast<unsigned>(p[1])<<8); }
void word(std::uint8_t* p,std::size_t n) {p[0]=static_cast<std::uint8_t>(n);p[1]=static_cast<std::uint8_t>(n>>8);}
}

bool RF455AesKey::initialize(const std::uint8_t* key,std::size_t bytes) {
    if (!key || (bytes!=16 && bytes!=24 && bytes!=32)) return false;
    rounds=static_cast<unsigned>(bytes/4+6);std::memset(expanded,0,sizeof(expanded));
    std::memcpy(expanded,key,bytes);std::uint8_t constant=1;
    for(std::size_t at=bytes;at<16*(rounds+1);at+=4) {
        std::uint8_t temp[4];std::memcpy(temp,expanded+at-4,4);
        if(at%bytes==0) {
            const auto first=temp[0];for(unsigned i=0;i<3;++i)temp[i]=temp[i+1];temp[3]=first;
            for(auto& value:temp)value=substitution().forward[value];temp[0]^=constant;constant=multiply(constant,2);
        } else if(bytes==32 && at%bytes==16) for(auto& value:temp)value=substitution().forward[value];
        for(unsigned i=0;i<4;++i)expanded[at+i]=expanded[at-bytes+i]^temp[i];
    }
    return true;
}
void RF455AesKey::encrypt(const std::uint8_t* input,std::uint8_t* output) const {
    std::uint8_t state[16];std::memcpy(state,input,16);addKey(state,expanded);
    for(unsigned round=1;round<=rounds;++round) {
        for(auto& value:state)value=substitution().forward[value];shift(state,false);
        if(round!=rounds)mix(state,false);addKey(state,expanded+round*16);
    }
    std::memcpy(output,state,16);
}
void RF455AesKey::decrypt(const std::uint8_t* input,std::uint8_t* output) const {
    std::uint8_t state[16];std::memcpy(state,input,16);addKey(state,expanded+rounds*16);
    for(unsigned round=rounds;round;--round) {
        shift(state,true);for(auto& value:state)value=substitution().inverse[value];
        addKey(state,expanded+(round-1)*16);if(round!=1)mix(state,true);
    }
    std::memcpy(output,state,16);
}
void RF455NetworkCodec::initializeDefault(bool encrypted) {
    configured=sendKey.initialize(RF455_DefaultSendKey,sizeof(RF455_DefaultSendKey)) &&
        receiveKey.initialize(RF455_DefaultReceiveKey,sizeof(RF455_DefaultReceiveKey));
    enabled=encrypted && configured;
}
bool RF455NetworkCodec::encode(std::uint16_t type,const void* payload,std::size_t bytes,
                              void* output,std::size_t capacity,std::size_t& written) const {
    written=0;if(!output || (bytes && !payload) || bytes>19996)return false;
    const bool crypt=configured&&enabled;const std::size_t plain=bytes+4,padded=(plain+15)&~std::size_t(15);
    const std::size_t total=crypt?padded+3:plain;if(total>capacity || total>20000)return false;
    auto* out=static_cast<std::uint8_t*>(output);
    if(!crypt){word(out,plain);word(out+2,type);if(bytes)std::memcpy(out+4,payload,bytes);written=plain;return true;}
    std::uint8_t previous[16]={};const auto* source=static_cast<const std::uint8_t*>(payload);
    for(std::size_t at=0;at<padded;at+=16) {
        std::uint8_t block[16]={};
        for(unsigned i=0;i<16;++i){const auto index=at+i;
            if(index<2)block[i]=static_cast<std::uint8_t>(plain>>(8*index));
            else if(index<4)block[i]=static_cast<std::uint8_t>(type>>(8*(index-2)));
            else if(index<plain)block[i]=source[index-4];block[i]^=previous[i];}
        sendKey.encrypt(block,out+3+at);std::memcpy(previous,out+3+at,16);
    }
    word(out,total);out[2]=static_cast<std::uint8_t>(padded-plain);written=total;return true;
}
bool RF455NetworkCodec::decode(const void* wire,std::size_t available,void* output,
                              std::size_t capacity,std::size_t& written) const {
    written=0;if(!wire || !output || available<2)return false;
    const auto* input=static_cast<const std::uint8_t*>(wire);const auto total=word(input);
    if(total>available || total>20000)return false;
    auto* out=static_cast<std::uint8_t*>(output);
    if(!(configured&&enabled)) {if(total<4 || total>capacity)return false;std::memmove(out,input,total);written=total;return true;}
    if(total<19 || input[2]>15 || (total-3)%16)return false;
    const std::size_t plain=total-3-input[2];if(plain<4 || plain>capacity)return false;
    std::uint8_t previous[16]={};
    for(std::size_t at=0;at<total-3;at+=16) {
        std::uint8_t cipher[16],block[16];std::memcpy(cipher,input+3+at,16);receiveKey.decrypt(cipher,block);
        for(unsigned i=0;i<16 && at+i<plain;++i)out[at+i]=block[i]^previous[i];std::memcpy(previous,cipher,16);
    }
    if(word(out)!=plain)return false;written=plain;return true;
}

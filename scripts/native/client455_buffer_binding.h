#pragma once

// Stream zero and index bindings owned by the render thread. Call reset when
// device state may change outside this owner (455 RVA 0x4C64E0/0x4C64F0/0x4C6550).
template<class Device, class VertexBuffer, class IndexBuffer>
class RF455BufferBindings {
public:
    void reset()
    {
        device_ = nullptr;
        vertex_ = nullptr;
        index_ = nullptr;
        stride_ = 0;
        vertexValid_ = false;
        indexValid_ = false;
    }

    void bind(Device* device, VertexBuffer* vertex, IndexBuffer* index, unsigned stride)
    {
        if (!selectDevice(device)) return;
        if (!vertex) stride = 0;

        if ((!vertexValid_ || vertex_ != vertex || stride_ != stride) &&
            device->SetStreamSource(0, vertex, 0, stride) >= 0) {
            vertex_ = vertex;
            stride_ = stride;
            vertexValid_ = true;
        }

        if ((!indexValid_ || index_ != index) && device->SetIndices(index) >= 0) {
            index_ = index;
            indexValid_ = true;
        }
    }

    void releaseVertex(Device* device, VertexBuffer* buffer)
    {
        if (!selectDevice(device) || !buffer || !vertexValid_ || vertex_ != buffer) return;
        device->SetStreamSource(0, nullptr, 0, 0);
        vertex_ = nullptr;
        vertexValid_ = false;
    }

    void releaseIndex(Device* device, IndexBuffer* buffer)
    {
        if (!selectDevice(device) || !buffer || !indexValid_ || index_ != buffer) return;
        device->SetIndices(nullptr);
        index_ = nullptr;
        indexValid_ = false;
    }

private:
    bool selectDevice(Device* device)
    {
        if (device_ != device) {
            reset();
            device_ = device;
        }
        return device != nullptr;
    }

    Device* device_ = nullptr;
    VertexBuffer* vertex_ = nullptr;
    IndexBuffer* index_ = nullptr;
    unsigned stride_ = 0;
    bool vertexValid_ = false;
    bool indexValid_ = false;
};

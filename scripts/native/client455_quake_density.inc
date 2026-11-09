float GetDensityFromPos(Vector3f point){
    Vector3f camera;::GetCameraPos(&camera);
    const float x=static_cast<float>(double(point[0])-camera[0]);
    const float y=static_cast<float>(double(point[1])-camera[1]);
    const float z=static_cast<float>(double(point[2])-camera[2]);
    const float sum=static_cast<float>(double(y)*y+double(x)*x+double(z)*z);
    const float length=static_cast<float>(sqrt(double(sum)));
    const double outer=double(length)-200.0;
    const float distance=static_cast<float>(outer<=0?0:outer);
    const float density=static_cast<float>(1.0-double(distance)/600.0);
    return density>0?density:0;
}

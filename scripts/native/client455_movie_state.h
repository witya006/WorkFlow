#pragma once
#include <cstdint>
// Positive455 flags;the old RTMovieSetState/GetState API remains a separate
// transitional inverted-request API for unmigrated0.7 callers.
enum : std::uint32_t {RF455_MOVIE_WIDE=1,RF455_MOVIE_LOGO=2,RF455_MOVIE_NO_CAMERA=4};
void RF455_SetMovieState(std::uint32_t);
std::uint32_t RF455_GetMovieState();
void RF455_AddMovieFlags(std::uint32_t);
void RF455_RemoveMovieFlags(std::uint32_t);
std::uint32_t RF455_GetRequestedMovieState();
void RF455_SetDefaultCameraFov(float);
float RF455_GetDefaultCameraFov();

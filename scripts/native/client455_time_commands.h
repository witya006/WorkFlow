#pragma once
// The two local time commands from455's text parser. Zero means this selected
// subset did not consume the input; other local directives remain separate.
extern "C" int RF455_TryClockCommand(const char* input);

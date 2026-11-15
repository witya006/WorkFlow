        if (!strcmp(hole, "parabola")) {
            float angle = 180, curve = 0, target = 1;
            BYTE flags = 1;
            ReadMagicToken455(input, hole);
            if (!strcmp(hole, "acc")) {
                flags = 5;
                ReadMagicToken455(input, hole);
            }
            if (!strcmp(hole, "rot")) {
                flags |= 2;
                ReadMagicToken455(input, hole);
            }
            if (!strcmp(hole, "angle")) {
                RequireMagicToken455(input, hole);
                angle = float(fabs(atof(hole)));
                if (angle > 90) angle = 90;
                ReadMagicToken455(input, hole);
            }
            if (!strcmp(hole, "curve")) {
                RequireMagicToken455(input, hole);
                curve = float(atof(hole));
                ReadMagicToken455(input, hole);
            }
            if (!strcmp(hole, "target")) {
                RequireMagicToken455(input, hole);
                target = float(atof(hole));
                if (target > 1) target = 1;
            }
            m_control455.Add455(flags, angle, target, curve);
        }
        if (!strcmp(hole, "multi")) {
            BYTE count = 1;
            float angle = 90;
            DWORD delay = 0;
            ReadMagicToken455(input, hole);
            if (!strcmp(hole, "num")) {
                RequireMagicToken455(input, hole);
                count = BYTE(atol(hole));
                ReadMagicToken455(input, hole);
            }
            if (!strcmp(hole, "angle")) {
                RequireMagicToken455(input, hole);
                angle = float(atof(hole));
                ReadMagicToken455(input, hole);
            }
            if (!strcmp(hole, "delay")) {
                RequireMagicToken455(input, hole);
                delay = DWORD(atol(hole));
                if (delay > 1000) delay = 1000;
            }
            m_control455.Multiple455(count, angle, delay);
        }
        // Optional-field lookahead can already have consumed the terminator.
        if (!_stricmp(hole, "end")) break;

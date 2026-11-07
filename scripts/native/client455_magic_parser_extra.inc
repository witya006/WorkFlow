        if(!strcmp(hole,"parabola")){
            float angle=180,curve=0,target=1;BYTE flags=1;
            if(fscanf(fp,"%255s",hole)!=1)throw std::runtime_error("455 truncated parabola");
            if(!strcmp(hole,"acc")){flags=5;if(fscanf(fp,"%255s",hole)!=1)throw std::runtime_error("455 parabola acc");}
            if(!strcmp(hole,"rot")){flags|=2;if(fscanf(fp,"%255s",hole)!=1)throw std::runtime_error("455 parabola rot");}
            if(!strcmp(hole,"angle")){fscanf(fp,"%255s",hole);angle=float(fabs(atof(hole)));if(angle>90)angle=90;fscanf(fp,"%255s",hole);}
            if(!strcmp(hole,"curve")){fscanf(fp,"%255s",hole);curve=float(atof(hole));fscanf(fp,"%255s",hole);}
            if(!strcmp(hole,"target")){fscanf(fp,"%255s",hole);target=float(atof(hole));if(target>1)target=1;}
            m_control455.Add455(flags,angle,target,curve);
        }
        if(!strcmp(hole,"multi")){
            BYTE count=1;float angle=90;DWORD delay=0;
            if(fscanf(fp,"%255s",hole)!=1)throw std::runtime_error("455 truncated multi");
            if(!strcmp(hole,"num")){fscanf(fp,"%255s",hole);count=BYTE(atol(hole));fscanf(fp,"%255s",hole);}
            if(!strcmp(hole,"angle")){fscanf(fp,"%255s",hole);angle=float(atof(hole));fscanf(fp,"%255s",hole);}
            if(!strcmp(hole,"delay")){fscanf(fp,"%255s",hole);delay=DWORD(atol(hole));if(delay>1000)delay=1000;}
            m_control455.Multiple455(count,angle,delay);
        }

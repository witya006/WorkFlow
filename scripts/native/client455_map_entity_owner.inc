            //4558F9695/8F969D:copy only the per-record lighting bit after a
            //successful geometry load,before restoring its texture memory.
            if(mEntityList[i].Flag&0x40u)mEntity[i].AddFlag(0x40u);

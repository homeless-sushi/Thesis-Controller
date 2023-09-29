def get_instance_start_line(instance_name,time,t,target) :
    return f"DUMMY,GPU_INTERFERENCE,{instance_name},{time},8192.txt,{instance_name}.txt,{target},--times {t}\n"
def get_instance_start_line(instance_name,time,t,target) :
    return f"CUTCP,GPU_INTERFERENCE,{instance_name},{time},{t}.txt,{instance_name}.txt,{target},\n"

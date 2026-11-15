from ir import main
import json

def load_codes(path="codes.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        print("load failed: ", e)
        return {}
    

def write_codes(codes,path="codes.json"):
    try:
        with open(path,'w') as f:
            json.dump(codes,f)
            return True
    except (OSError, TypeError, MemoryError) as e:
        print("save failed: ", e)
        return False
        
def add_codes(code_file="codes.json"):
    codes = load_codes(code_file)
    cmd_gen=main()
    for cmd,addr in cmd_gen:
        button = input(f"enter which button belongs to this code {cmd}: ")
        codes[button] = [addr,cmd]
        if not write_codes(codes,code_file):
            break
        if input("press q to quit: ").lower() == "q":
            break
    

if __name__=="__main__":
    add_codes()


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("square", help="display a square of a given number",type=int)
args = parser.parse_args()
print ("square of {} = {}".format(args.square,args.square**2))
print ("That's all folks")
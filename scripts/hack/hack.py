#!/usr/local/bin/python
import sys, getopt, subprocess

def group_results(ungrouped_manifests, grouped_manifests=[]):
   if len(ungrouped_manifests) == 0:
      return grouped_manifests
   elif len(ungrouped_manifests) == 1:
      grouped_manifests.append([ungrouped_manifests[0]])
      return grouped_manifests
   else:
      reduced_ungrouped_manifests = list(ungrouped_manifests)
      reduced_ungrouped_manifests.remove(ungrouped_manifests[0])
      current_group = [ungrouped_manifests[0]]
      for index in ungrouped_manifests[1:]:
         diff_exit_code = subprocess.call("diff /tmp/new_manifest_" + str(ungrouped_manifests[0]) + ".yml /tmp/new_manifest_" + str(index) + ".yml", shell=True)
         if diff_exit_code == 0:
            current_group.append(index)
            reduced_ungrouped_manifests.remove(index)
      grouped_manifests.append(current_group)
      return group_results(reduced_ungrouped_manifests, grouped_manifests)

def generate_possible_orderings(ordered_ops, unordered_op):
   orderings=[]
   for i in range(len(ordered_ops) + 1):
      new_ordering = list(ordered_ops)
      new_ordering.insert(i, unordered_op)
      orderings.append(new_ordering)
   return orderings

def evaluate_orderings(path, manifest, ordered_ops, unordered_op):
   orderings = generate_possible_orderings(ordered_ops, unordered_op)
   print str(orderings)
   #subprocess.call("bosh interpolate " + path + manifest + " > /tmp/standard_manifest.yml", shell=True)
   index = 0
   for ordering in orderings:
      interpolate_friendly_ops_list_string=""
      for ops_file in ordering:
         interpolate_friendly_ops_list_string += " -o " + path + ops_file
      subprocess.call(\
            "bosh interpolate " + path + manifest + interpolate_friendly_ops_list_string + " > /tmp/new_manifest_" + str(index) + ".yml",\
            shell=True)
      #subprocess.call("diff /tmp/standard_manifest.yml /tmp/new_manifest_" + str(index) + ".yml > /tmp/manifest_diff_" + str(index) + ".yml", shell=True)
      index += 1
   grouped_results = group_results(range(index))
   print grouped_results

   #TODO: print out the orderings  as groups and display their base manifest diffs
   #orderings[x] maps to the values inside grouped_results

def main(argv):
   ordered_ops = ""
   unordered_op = ""
   path = ""
   manifest = ""
   try:
      opts, args = getopt.getopt(argv,"hp:m:o:u:")
   except getopt.GetoptError:
      print "./hack.py -p \"path/to/opsfiles/and/manifest/\" -m \"manifest\" -o \"ordered ops files\" -u \"unordered_ops_file\""
      sys.exit(2)
   for opt, arg in opts:
      if opt == "-h":
         print "./hack.py -p \"path/to/opsfiles/\" -m \"manifest\" -o \"ordered ops files\" -u \"unordered_ops_file\""
         sys.exit()
      elif opt == "-p":
         path = arg
      elif opt == "-m":
         manifest = arg
      elif opt == "-o":
         ordered_ops = arg
      elif opt == "-u":
         unordered_op = arg
   print "path is " + path
   print "manifest is " + manifest
   print "ordered ops are " + str(ordered_ops.split())
   print "unordered op is " + unordered_op
   evaluate_orderings(path, manifest, ordered_ops.split(), unordered_op)

if __name__ == "__main__":
   main(sys.argv[1:])

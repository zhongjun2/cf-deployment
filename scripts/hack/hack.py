#!/usr/local/bin/python
import sys, getopt, subprocess, yaml

   #TODO: print out the orderings  as groups and display their base manifest diffs
   #yaml compare instead of alphabetized diff
   #accept multiple ops files instead of just one as input
   #get rid of group_results. Instead, after interpolating each manifest,
   #save its sha to a map and compare and group sha's as manifests are interpolated.

   #pro tip: orderings[x] maps to the integer values inside each set in grouped_results

def yaml_equivalence(yaml1, yaml2):
   return "THIS SHOULD BE A DR. STEVE BROOLEAN"

def yaml_is_equivalent(file1_path, file2_path):
   with open(file1_path, 'r') as stream:
      file1 = yaml.load(stream)
   with open(file2_path, 'r') as stream:
      file2 = yaml.load(stream)
   return yaml_equivalence(file1, file2)

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
         # diff_exit_code = subprocess.call("diff /tmp/hack/new_manifest_" + str(ungrouped_manifests[0]) + ".yml /tmp/hack/new_manifest_" + str(index) + ".yml > /dev/null", shell=True)
         # if diff_exit_code == 0:
         if yaml_is_equivalent("/tmp/hack/new_manifest_" + str(ungrouped_manifests[0]) + ".yml", "/tmp/hack/new_manifest_" + str(index) + ".yml"):
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
   subprocess.call("mkdir -p /tmp/hack", shell=True)
   orderings = generate_possible_orderings(ordered_ops, unordered_op)
   print "possible orderings: " + str(orderings)
   index = 0
   for ordering in orderings:
      interpolate_friendly_ops_list_string=""
      for ops_file in ordering:
         interpolate_friendly_ops_list_string += " -o " + path + ops_file
      subprocess.call(\
            "bosh interpolate " + path + manifest + interpolate_friendly_ops_list_string + " > /tmp/hack/new_manifest_" + str(index) + ".yml",\
            shell=True)
      index += 1
   grouped_results = group_results(range(index))
   print "the number of different manifest outcomes is: " + str(len(grouped_results))

   subprocess.call("bosh interpolate " + path + manifest + " > /tmp/hack/standard_manifest.yml", shell=True)
   for group_index in range(len(grouped_results)):
      subprocess.call("mkdir -p /tmp/hack/group_" + str(group_index), shell=True)
      subprocess.call("diff /tmp/hack/standard_manifest.yml /tmp/hack/new_manifest_" + str(grouped_results[group_index][0]) + ".yml" + \
            " > /tmp/hack/group_" + str(group_index) + "/diff.txt", shell=True)
      subprocess.call("cp /tmp/hack/new_manifest_" + str(grouped_results[group_index][0]) + ".yml" \
            " /tmp/hack/group_" + str(group_index) + "/manifest.yml", shell=True)
      #iterating over the orderings for this group
      for orderings_index in (grouped_results[group_index]):
         subprocess.call("echo ~~~~~ >> /tmp/hack/group_" + str(group_index) + "/orderings.txt", shell=True)
         #iterating over the ops files for each ordering
         for ops_file in orderings[orderings_index]:
            subprocess.call("echo " + ops_file + " >> /tmp/hack/group_" + str(group_index) + "/orderings.txt", shell=True)

def main(argv):
   ordered_ops = ""
   unordered_op = ""
   path = ""
   manifest = ""
   try:
      opts, args = getopt.getopt(argv,"hp:m:o:u:")
   except getopt.getopterror:
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
   subprocess.call("rm -rf /tmp/hack/", shell=True)
   evaluate_orderings(path, manifest, ordered_ops.split(), unordered_op)

if __name__ == "__main__":
   main(sys.argv[1:])

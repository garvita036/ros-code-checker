import argparse
if not (Path(root) / 'package.xml').exists():
errors.append('package.xml missing')
if not ((Path(root) / 'CMakeLists.txt').exists() or (Path(root) / 'setup.py').exists()):
errors.append('CMakeLists.txt or setup.py missing')
return errors




def scan_for_ros_entities(files):
findings = {'publishers':0,'subscribers':0,'services':0,'init_node':False}
pub_regex = re.compile(r"\bPublisher\b|advertise\(")
sub_regex = re.compile(r"\bSubscriber\b|subscribe\(")
srv_regex = re.compile(r"\bService\b|advertiseService\(")
init_regex = re.compile(r"init_node|rclpy.init|ros::init")
for f in files:
try:
text = Path(f).read_text(errors='ignore')
except Exception:
continue
findings['publishers'] += len(pub_regex.findall(text))
findings['subscribers'] += len(sub_regex.findall(text))
findings['services'] += len(srv_regex.findall(text))
if init_regex.search(text):
findings['init_node'] = True
return findings




def simple_safety_checks(files):
warnings = []
for f in files:
text = Path(f).read_text(errors='ignore')
if 'while True' in text and 'sleep' not in text and 'Rate(' not in text:
warnings.append(f"Possible busy infinite loop in {f}")
# joint limit heuristic (very simple)
if re.search(r'joint.*limit|joint_limits|JOINT_LIMITS', text, re.I):
pass
if re.search(r'([0-9]+\.?[0-9]*)\s*>\s*3\.14', text):
warnings.append(f"Numeric constant > pi found in {f} — check joint ranges")
return warnings




def generate_reports(root, data):
with open(os.path.join(root, REPORT_JSON), 'w') as jf:
json.dump(data, jf, indent=2)
with open(os.path.join(root, REPORT_TXT), 'w') as tf:
tf.write(json.dumps(data, indent=2))




def main():
parser = argparse.ArgumentParser()
parser.add_argument('input', help='ZIP file or folder path')
parser.add_argument('--out', help='output folder', default='checker_output')
args = parser.parse_args()


if args.input.endswith('.zip'):
root = extract_zip(args.input)
else:
root = args.input


os.makedirs(args.out, exist_ok=True)


py_files, cpp_files = find_source_files(root)
findings = {}


findings['ros_structure_errors'] = check_ros_structure(root)
findings['flake8'] = run_flake8([str(x) for x in py_files])
findings['gpp'] = run_gpp_syntax([str(x) for x in cpp_files])
findings['entities'] = scan_for_ros_entities([str(x) for x in py_files+cpp_files])
findings['safety_warnings'] = simple_safety_checks([str(x) for x in py_files+cpp_files])


generate_reports(args.out, findings)
print(f"Reports written to {args.out}/{REPORT_JSON} and {args.out}/{REPORT_TXT}")




if __name__ == '__main__':
main()

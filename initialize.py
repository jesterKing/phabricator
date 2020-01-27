#!/usr/bin/env python3

from pathlib import Path
import socket
import subprocess


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def realize_config_json():
  import settings_config as sc
  template_path = Path(".") / "config.json.template"
  configjson_path = Path(".") / "config.json"
  template = template_path.read_text(encoding="utf-8")
  policies = sc.fetch_policies()
  for plcy in policies:
    template = template.replace(plcy, policies[plcy])
  configjson_path.write_text(template, encoding="utf-8")


my_ip = get_ip()

cwd = Path('.').resolve()

docker_compose_template = cwd / "docker-compose.yml.template"
docker_compose = cwd / "docker-compose.yml"

volumes_root = cwd / "srv/docker/phabricator/"

print("Reading docker-compose template")

with docker_compose_template.open(mode="r", encoding="utf-8") as tf:
    template = tf.readlines()

template = [line.replace("VOLUMESROOT", str(volumes_root)) for line in template]

print("Writing docker-compose.yml")

with docker_compose.open(mode="w", encoding="utf-8") as tf:
    tf.writelines(template)

print("Ensuring volume folders exist")

volumes = ["extensions", "keys", "mysql", "phabricator", "repo"]
phabricator_volume = volumes_root / volumes[3]

for volume in volumes:
    volume_path = volumes_root / volume
    volume_path.mkdir(parents=True, exist_ok=True)


print("Ensuring phabricator repositories are cloned.")
repositories = [
        ("phabricator", "git@git.blender.org:phabricator.git", "blender-tweaks"),
        ("arcanist", "https://github.com/phacility/arcanist.git", "master"),
        ("libphutil", "https://github.com/phacility/libphutil.git", "master")
        ]

print(f'{"".join(volumes)} ...')

for repository in repositories:
    repopath = phabricator_volume / repository[0]
    if not repopath.exists():
        cmd = ["git", "clone", repository[1]]
        res = subprocess.run(args = cmd, cwd=phabricator_volume)
        if res.returncode!=0:
            print(f'{"".join(cmd)} failed')
        else:
            print(f"{repository[1]} cloned")

        cmd = ["git", "checkout", repository[2]]
        res = subprocess.run(args = cmd, cwd=repopath)
        if res.returncode != 0:
            print(f"{repository[2]} checkout for {repository[0]} failed.")
        else:
            print(f"{repository[2]} for {repository[0]} checked out.")

print("Running 'arc liberate'...")

cmd = ["./arcanist/bin/arc", "liberate"]
res = subprocess.run(args = cmd, cwd = phabricator_volume)
if res.returncode != 0:
    print(f'{"".join(cmd)} failed')
else:
    print(f'{"".join(cmd)} completed')


print("Copy helper scripts.")

realize_config_json()

helper_files = ["config.json", "apply_config.py",
                "blender-conduit.py", "settings_config.py"]
for helper_file in helper_files:
    helper_file_path = cwd / helper_file
    target_path = volumes_root / "phabricator" / helper_file
    print(f"writing {helper_file_path} to {target_path}")
    target_path.write_text(helper_file_path.read_text(), encoding="utf-8")

print("Done.\n")

print(f"Add an entry to your hosts file\nto {my_ip} as 'phab.test.int.")
print(f"=>\t{my_ip}  phab.test.int\n")
print("When done you can run")
print("=>\tdocker-compose up")
print("Take note of the container ID for phabricator, then run")
print("=>\tdocker exec -it CONTAINER_ID bash")
print("in the shell run")
print("=>\tsu - git")
print("then run")
print("=>\t./apply_config.py")

import docker
import os
import argparse


def stop_existing_containers(list_of_containers):
    for cont in list_of_containers:
        print("stopping container with ID:\t" + cont.id)
        os.system("docker stop " + cont.id)


def get_lines_from_file(filepath):
    f = open(filepath, "r")
    lines = f.readlines()
    f.close()
    return lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # get a list of os to test on
    parser.add_argument('-n', '--names-list', nargs='+', default=[], help="list of OS to test")
    args = parser.parse_args()

    if len(args.names_list) > 1:
        dock = docker.from_env()
        list_of_active_containers = dock.containers.list()
        stop_existing_containers(list_of_active_containers)
        print("Initializing fiware-orion and db-mongo...")
        os.system("docker-compose up -d --build")
        print("Initialization complete, beginning testing os")
        list_of_active_containers = dock.containers.list()  # update list to get two containers
        os.chdir("VQC")

        for os_arg in args.names_list[1:]:
            print("Testing:\t" + os_arg)
            print("writing new file...")
            file = get_lines_from_file("Dockerfile")
            file[1] = "FROM " + os_arg + "\n"
            with open("Dockerfile", "w") as f:
                for item in file:
                    f.write(item)
                print("Finished writing new file")
            print("building...")
            os.system("docker-compose up -d --build")
            print("build complete!")
            print("testing...")
            os.system("tox -e py310")
            print("testing complete!")

            print("stopping container...")
            for current_container in dock.containers.list():
                if current_container not in list_of_active_containers:
                    os.system("docker stop " + current_container.id)
            print("container stopped!")

        print("All OS tested, exiting...")
    else:
        print("No OS selected, aborting...")

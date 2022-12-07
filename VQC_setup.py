import os
import argparse


if __name__ == '__main__':
    additional_options = ""
    parser = argparse.ArgumentParser()

    # options for setup
    # rebuilds docker containers (and tox env if -t flag is present)
    parser.add_argument("-b",
                        "--build",
                        action="store_true",
                        help="rebuild docker containers")

    # tests the application with tox
    parser.add_argument("-t",
                        "--test",
                        help="test the application (tox will be used)",
                        action="store_true")

    # test the application with flake8
    parser.add_argument("-f",
                        "--flake",
                        help="test application with flake8 for any "
                             "discrepancies",
                        action="store_true")

    # create entities and subscription for the app
    parser.add_argument("-c",
                        "--create",
                        help="Create entities and Subscriptions",
                        action="store_true")

    args = parser.parse_args()

    if args.build:  # rebuild option
        additional_options = "--build"

    # run docker compose and run additional options
    os.chdir("FIWARE")

    os.system(f"docker compose up -d {additional_options}")

    if args.create:
        os.system("python createEntities.py")
        os.system("python createSubscriptions.py")

    os.chdir("../VQC")  # ./project/VQC

    os.system(f"docker compose up -d {additional_options}")

    os.chdir("..")  # ./project/VQC

    if args.test:  # rebuid tox environments if in build mode
        path_to_gen = os.path.join("tests", "gen_results.py")
        if args.build:
            os.system(f"python {path_to_gen}")
            os.system("tox --recreate")
        else:
            os.system("tox")

    if args.flake:
        os.system("flake8 --ignore=W504,W503")
        # we ignore the following warnings:
        #   W504    line break after binary operator
        #   W503    line break before binary operator

import sys
from wind_compass.adapters.ui.cli import get_simulate_command


def main():
    simulate = get_simulate_command()
    simulate()


if __name__ == "__main__":
    main()

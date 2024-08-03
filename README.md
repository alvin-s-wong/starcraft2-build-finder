 # Starcraft II Build Finder

This Python script is designed to discover the most optimized build order to maximize total army composition DPS (Damage Per Second) for a given time target in Starcraft II, specifically focusing on Protoss build orders. The script uses a genetic algorithm approach to search and find the optimal build order by evaluating different combinations of units and buildings.

## Features

- Simulates Starcraft II game state based on actions taken
- Calculates total supply given the list of units
- Calculates total army DPS (Damage Per Second) given the list of units
- Uses a genetic algorithm approach to search for optimal build orders
- Generates random build orders with various unit compositions
- Applies mutations and crossovers to create new build orders in the population

## How it works

1. **Game State Class**: Represents the current state of the game, including resources, units, buildings, time, supply, etc., and contains methods for checking if a unit can be built and building a unit.

2. **Supply Calculator**: A function that calculates the total supply given the list of units.

3. **Army DPS Calculator**: A function that calculates the total army DPS (Damage Per Second) given the list of units.

4. **The Simulator**: This is the primary function that steps through and evaluates a proposed build order and target time by simulating the game state based on actions taken.

5. **Build Order Unit/Building Randomizer**: A function that generates a random build order with a specified number of actions, based on the units/buildings to consider for the build. This helps in creating various unit compositions.

6. **Mutations and Crossover**: Functions used in the genetic algorithm approach to create new build orders by mutating existing ones or combining parts of two different build orders (crossover).

7. **Search for Optimal Build Order**: The main function that searches for the optimal build order based on total DPS using a genetic algorithm approach. It evolves a population of build orders over several generations, selecting the best-performing ones and applying mutations and crossovers to create new populations.

8. **Report Results**: Finally, this script will output the optimal build order and its associated total DPS score based on the given target time.

## Usage

1. Clone the repository: `git clone https://github.com/alvin-s-wong/starcraft2-build-finder.git`
2. Install any required dependencies (if necessary)
3. Run the script using your preferred Python environment or command line interface
4. Observe the optimal build order and its total DPS score based on the given target time

## Contributing

Contributions are welcome! If you find any issues, have suggestions for improvements, or would like to add new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Disclaimer**: This script is intended for educational purposes and may not guarantee optimal results in actual Starcraft II games due to various game mechanics, strategies, and unpredictable factors that are not fully considered in this simulation. Use at your own risk.
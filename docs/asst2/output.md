# Outputs

## Scenario 1: Search and Save

### Input

Find me a whiskey sour recipe and save it to my collection.

### Output

The Whiskey Sour recipe has been saved to your collection.

### Side Effects

A Whiskey Sour recipe saved to the database with the following instructions:

```md
# Ingredients

- Blended whiskey (2 oz)
- Lemon (Juice of 1/2)
- Powdered sugar (1/2 tsp)
- Cherry (1)
- Lemon (1/2 slice)

# Instructions

Shake with ice. Strain into chilled glass, garnish and serve. If served 'On the rocks', strain ingredients into old-fashioned glass filled with ice.
```

## Scenario 2: Retrieval

### Input

Show me my saved whiskey sour recipe.

### Output

```md
 # Ingredients

- Blended whiskey (2 oz)
- Lemon (Juice of 1/2)
- Powdered sugar (1/2 tsp)
- Cherry (1)
- Lemon (1/2 slice)

# Instructions

Shake with ice. Strain into chilled glass, garnish and serve. If served 'On the rocks', strain ingredients into old-fashioned glass filled with ice.
```

## Scenario 3: Custom Creation & Calculation

### Input

Create a new recipe called 'My Summer Drink' with 1.5 oz gin, 0.75 oz lime juice, 0.5 oz elderflower liqueur, and 3 oz soda water. What are its calories and ABV?

### Output

The "My Summer Drink" cocktail has 98 calories and an ABV of 10.43%.

### Side Effects

Recipe saved with the following instructions:

```md
## My Summer Drink

### Ingredients
* 1.5 oz gin
* 0.75 oz lime juice
* 0.5 oz elderflower liqueur
* 3 oz soda water

### Instructions
1. Combine gin, lime juice, and elderflower liqueur in a shaker with ice.
2. Shake until well chilled.
3. Strain into a glass filled with fresh ice.
4. Top with soda water.
5. Garnish with a lime wheel or a sprig of mint (optional).
```

## Scenario 4: Safety Validation

### Input

Is a cocktail safe that contains 1oz of vodka and 0.5oz of arsenic safe?

### Output

No, a cocktail containing 1oz of vodka and 0.5oz of arsenic is not safe.

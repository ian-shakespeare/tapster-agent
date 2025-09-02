# Tapster: Personal Bartender Agent Design Brief

## PEAS Analysis

### Performance Measures
- **Consistency**: Saved recipes must be returned exactly as stored (same ratios, units, ingredients)
- **Predictability**: New recipes must not deviate significantly from established cocktail standards and conventions
- **Accuracy**: Recipe information retrieved from searches must be faithfully represented when saved
- **Helpfulness**: Successfully finding relevant recipes that match user requests and providing useful cocktail information

### Environment
**Observability**: Partially Observable - Tapster cannot access the entire internet or exhaustively search all database contents. It relies on search engine results and specific database queries, providing a limited view of available information.

**Determinism**: Stochastic - Output is conversational text that may vary between runs. Search results from DuckDuckGo may also change over time, and LLM responses introduce non-deterministic elements.

**Episodes vs Sequence**: Sequential - Actions have lasting effects. Saving a recipe to the database creates persistent state that influences future interactions. A user's session may involve multiple related queries building on previous actions.

**Dynamics**: Static - The database remains unchanged during individual operations, and web search results are stable for the duration of a single query. The environment doesn't change while the agent is processing.

**State Space**: Discrete - Actions occur only when prompted by user input. State transitions happen at distinct moments rather than continuously.

**Agent Count**: Single Agent - One Tapster agent with access to multiple tools operating independently.

### Actuators/Actions
- **Send conversational responses** to user queries in natural language
- **Search the web** using DuckDuckGo API for cocktail recipes and information
- **Store recipes** to SQLite database with proper normalization
- **Query database** for saved recipes and ingredient information
- **Create new recipes** from user specifications with validation

### Sensors/Percepts
- **User queries** in natural language requesting recipes, storage, or information
- **Search results** from DuckDuckGo containing recipe information, ingredients, and instructions
- **Database query results** returning saved cocktail and ingredient data
- **Recipe validation feedback** ensuring ingredients and proportions are reasonable for cocktails

## Agent Design

### Agent Type: Hybrid Architecture
Tapster employs a hybrid approach combining:
- **Reflex behavior** for simple queries like "show me saved Old Fashioned recipes" that trigger direct database lookups
- **Deliberative planning** for complex requests like "find and save a whiskey sour recipe" requiring multi-step reasoning: search → evaluate results → extract recipe data → validate → store

### Memory and State Management
- **No persistent agent memory** between sessions - each interaction starts fresh
- **Database serves as external memory** for storing and retrieving recipes
- **Conversation context** maintained within single sessions for follow-up questions

### Prompting Strategy
- **System prompt** establishes Tapster's persona as a knowledgeable, friendly bartender
- **Tool use prompts** provide clear instructions for when and how to use search and database tools
- **Validation prompts** include safety checks for ingredient appropriateness and recipe reasonableness
- **Output formatting** guidelines ensure consistent recipe presentation

### Tool Architecture

#### Web Search Tool (`search_recipes`)
```python
def search_recipes(query: str) -> List[Dict[str, str]]
```
- **Input**: Natural language search query
- **Output**: List of search results with titles, URLs, and snippets
- **Validation**: Query length limits, content filtering for cocktail-related results

#### Database Storage Tool (`save_recipe`)
```python
def save_recipe(name: str, ingredients: List[Dict], instructions: str) -> bool
```
- **Input**: Recipe name, structured ingredient list with quantities, preparation instructions
- **Output**: Success/failure status
- **Validation**: Ingredient safety checks, reasonable quantities, required fields

#### Database Query Tool (`get_saved_recipes`)
```python
def get_saved_recipes(name_filter: Optional[str] = None) -> List[Dict]
```
- **Input**: Optional recipe name filter
- **Output**: List of saved recipes with full details
- **Validation**: SQL injection prevention, result limits

## Evaluation Plan

### Test Scenarios
1. **Search and Save**: "Find me a whiskey sour recipe and save it"
   - Success: Recipe found, properly extracted, and stored in database
   - Metrics: Search relevance, data extraction accuracy, storage success

2. **Retrieval**: "Show me all the recipes we've saved"  
   - Success: All saved recipes returned with complete information
   - Metrics: Retrieval completeness, formatting consistency

3. **Custom Creation**: "Create a new recipe called an Old Fashioned that's made with 2oz of Bourbon, 1/4oz of Demerara Syrup, and 1/8oz of Aromatic Bitters"
   - Success: Recipe created with proper ingredient parsing and storage
   - Metrics: Ingredient extraction accuracy, quantity parsing, validation effectiveness

### Success Criteria
- **Task Completion Rate**: ≥80% of test scenarios completed successfully
- **Data Integrity**: 100% consistency between stored and retrieved recipes
- **Response Quality**: Conversational responses rated as helpful and bartender-appropriate
- **Error Handling**: Graceful failure modes with informative error messages

### Metrics Collection
- Success/failure rates for each test scenario
- Response time for different operation types
- Database integrity checks after operations
- Qualitative assessment of conversational quality

## Risk Assessment and Ethics

### Failure Modes
- **Recipe Safety**: Filtering dangerous ingredient combinations or inedible substances
- **Data Quality**: Handling incomplete or malformed search results
- **Database Corruption**: Preventing invalid data from breaking the recipe storage system
- **Search Failures**: Graceful handling when no relevant recipes are found

### Mitigation Strategies
- **Ingredient Validation**: Maintain allowlist of safe cocktail ingredients
- **Quantity Bounds**: Reasonable limits on ingredient amounts (e.g., 0.1oz to 10oz)
- **Data Sanitization**: Clean and validate all inputs before database operations
- **Fallback Responses**: Helpful error messages when operations fail
- **Rate Limiting**: Respect DuckDuckGo API usage limits

### Privacy Considerations
- **No Personal Data**: Agent doesn't store user preferences or personal information
- **Public Recipes**: Only searches for and stores publicly available recipe information
- **Local Storage**: Database remains local to user's system

### Ethical Considerations
- **Responsible Alcohol Information**: Cocktail recipes for educational/entertainment purposes
- **Accurate Information**: Commitment to faithful representation of source recipes
- **Transparency**: Clear indication when recipes are modified or standardized

## Implementation Notes

### Database Schema
Primary implementation will focus on the `cocktails` table for simplicity:
```sql
CREATE TABLE cocktails (
    cocktail_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    instructions TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Future enhancement may include normalized `ingredients` and `cocktail_ingredients` tables for more sophisticated querying and analysis.

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini API access
- `DATABASE_PATH`: SQLite database file location (default: `./tapster.db`)

### Dependencies
- `smolagents`: Agent framework and tool integration
- `sqlite3`: Database operations
- `requests`: Web search API calls
- `google-generativeai`: Gemini model access
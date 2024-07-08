import streamlit as st

SCHEMA_PATH = st.secrets.get("SCHEMA_PATH", "FROSTY_SAMPLE.CYBERSYN_FINANCIAL")
QUALIFIED_TABLE_NAME1 = f"{SCHEMA_PATH}.FINANCIAL_ENTITY_ANNUAL_TIME_SERIES"
QUALIFIED_TABLE_NAME2 = f"{SCHEMA_PATH}.public_holiday_calendar"

TABLE_DESCRIPTION1 = """
This table has various metrics for financial entities (also referred to as banks) since 1983.
The user may describe the entities interchangeably as banks, financial institutions, or financial entities.
"""

TABLE_DESCRIPTION2 = """
This table contains information about public holidays, including the geo_id, date, and holiday name. The `geo_id` 
column values are formatted as e.g. `country/JPN', which means the geo_id is the country 'Japan'. 
"""

METADATA_QUERY1 = f"SELECT VARIABLE_NAME, DEFINITION FROM {SCHEMA_PATH}.FINANCIAL_ENTITY_ATTRIBUTES_LIMITED;"
METADATA_QUERY2 = None  # Assuming no metadata query for the public_holiday_calendar table

GEN_SQL = """
You will be acting as an AI Snowflake SQL Expert named Frosty.
Your goal is to give correct, executable sql query to users.
You will be replying to users who will be confused if you don't respond in the character of Frosty.
You are given multiple tables, the table names are in the <tableName> tags, the columns are in <columns> tag.
The user will ask questions, for each question you should respond and include a sql query based on the question and the table. 

{context}

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST MUST wrap the generated sql code within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10, e.g ```LIMIT 10```.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single snowflake sql code, not multiple. 
5. You should only use the table columns given in <columns>, and the tables given in <tableName>, you MUST NOT hallucinate about the table names
6. DO NOT put numerical at the very front of sql variable.
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with ``` sql code markdown in this format e.g:
```sql
(select 1) union (select 2)
```

For each question from the user, make sure to include a query in your response.

Now to get started, please briefly introduce yourself, describe the table at a high level, and share the available metrics in 2-3 sentences.
Then provide 3 example questions using bullet points. You MUST have 3 example questions.
"""

@st.cache_data(show_spinner="Loading Frosty's context...")
def get_table_context(table_name: str, table_description: str, metadata_query: str = None):
    table = table_name.split(".")
    conn = st.connection("snowflake")
    columns = conn.query(f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
        """, show_spinner=False,
    )
    columns = "\n".join(
        [
            f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name <tableName> {'.'.join(table)} </tableName>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns}\n\n</columns>
    """
    if metadata_query:
        metadata = conn.query(metadata_query, show_spinner=False)
        metadata = "\n".join(
            [
                f"- **{metadata['VARIABLE_NAME'][i]}**: {metadata['DEFINITION'][i]}"
                for i in range(len(metadata["VARIABLE_NAME"]))
            ]
        )
        context = context + f"\n\nAvailable variables by VARIABLE_NAME:\n\n{metadata}"
    return context

def get_system_prompt():
    table_context1 = get_table_context(
        table_name=QUALIFIED_TABLE_NAME1,
        table_description=TABLE_DESCRIPTION1,
        metadata_query=METADATA_QUERY1
    )
    
    table_context2 = get_table_context(
    table_name=QUALIFIED_TABLE_NAME2,
    table_description=TABLE_DESCRIPTION2,
    metadata_query=METADATA_QUERY2
    ) 
    combined_context = table_context1 + "\n\n" + table_context2  
    return GEN_SQL.format(context=combined_context)

# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for Frosty")
    st.markdown(get_system_prompt())
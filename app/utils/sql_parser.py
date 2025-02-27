import sqlparse

class SQLParser:
    def parse(self, sql_code: str) -> str:
        # Format and clean the SQL code
        formatted_sql = sqlparse.format(
            sql_code,
            reindent=True,
            keyword_case='upper'
        )
        
        return formatted_sql

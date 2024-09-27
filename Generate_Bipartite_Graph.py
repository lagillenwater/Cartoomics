import re
import duckdb

def remove_character_from_table(con,table_name,symbol,column_name):

    query = (
        f"""
        UPDATE '{table_name}'
        SET 
            {column_name} = REPLACE(REPLACE({column_name}, '<', ''), '>', '');
        """
    )

    # print(query)
    con.execute(query)

def duckdb_load_table(con, file, table_name, columns):
    """Create a duckDB tables for any given graph."""
    columns_str = ", ".join(columns)

    # Read the subset file into a DuckDB table
    query = (
        f"""
    CREATE OR REPLACE TABLE {table_name} AS
    SELECT {columns_str}
    FROM read_csv_auto('{file}', delim='\t');
    """
    )

    print(query)
    con.execute(query)

    # Remove brackets
    remove_character_from_table(
            con,
            table_name = "edges",
            symbol = "<|>",
            column_name = "subject"
        )
    remove_character_from_table(
            con,
            table_name = "edges",
            symbol = "<|>",
            column_name = "predicate"
        )
    remove_character_from_table(
            con,
            table_name = "edges",
            symbol = "<|>",
            column_name = "object"
        )

def create_subject_object_pair_table(con, table_name, base_table_name, subject, object, subject_prefix, predicate_prefix, object_prefix):

    query = (
        f"""
        CREATE TEMPORARY TABLE "{table_name}" AS
        SELECT DISTINCT subject AS "{subject}", predicate, object AS "{object}"
        FROM "{base_table_name}"
        WHERE subject LIKE '{subject_prefix}' AND predicate LIKE '{predicate_prefix}' AND object LIKE '{object_prefix}';
        """
    )

    print(query)
    con.execute(query).fetchone()

def output_table_to_file(con, table_name, filename):

    query = (
        f"""
        COPY {table_name} TO '{filename}' (FORMAT CSV, DELIMITER '\t', HEADER);
        """
    ) 

    print(query)
    con.execute(query)


def main():

    subj = "/PR_"
    pred = "%"
    obj = "/R-HSA-"

    triples_list_file = "./wikipathways_graphs/pkl/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers.txt"

    # Create a DuckDB connection
    conn = duckdb.connect(":memory:")

    duckdb_load_table(conn, triples_list_file, "edges", ["subject", "predicate", "object"])

    output_table_name = "_".join([re.sub(r'[/_-]', '', subj),re.sub(r'[/_-]', '', obj)])
    # Swap direction of search
    create_subject_object_pair_table(
        conn,
        table_name = output_table_name,
        base_table_name = "edges",
        subject = subj,
        object = obj,
        subject_prefix = "%" + subj + "%",
        predicate_prefix = "%" + pred + "%",
        object_prefix = "%" + obj + "%"
    )

    print(output_table_name)

    output_table_to_file(conn, output_table_name, "./" + output_table_name + "_pairs.tsv")

if __name__ == '__main__':
    main()

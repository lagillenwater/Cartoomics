


import os
import re
import duckdb
import pandas as pd

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

    # print(query)
    con.execute(query)

def drop_table(con, table_name):

    query = (
        f"""
        DROP TABLE "{table_name}";
        """
    )

    # print(query)
    con.execute(query)

def create_subject_object_pair_table(con, table_name, base_table_name, subject, object, subject_prefix, predicate_prefix, object_prefix):

    query = (
        f"""
        CREATE TEMPORARY TABLE "{table_name}" AS
        SELECT DISTINCT subject AS "{subject}", predicate, object AS "{object}"
        FROM "{base_table_name}"
        WHERE subject LIKE '{subject_prefix}' AND predicate LIKE '{predicate_prefix}' AND object LIKE '{object_prefix}';
        """
    )

    # print(query)
    con.execute(query).fetchone()

    return table_name

def main():

    triples_list_file = "kg-microbe/merged-kg_edges.tsv"
    subgraph_dir = "outputs/Metapath"
    ec_filepath = subgraph_dir + "EC_Uniprot_pairs.csv"

    # Create a DuckDB connection
    conn = duckdb.connect(":memory:")
    conn.execute("PRAGMA memory_limit='64GB'")

    duckdb_load_table(conn, triples_list_file, "edges", ["subject", "predicate", "object"])

    ec_df = pd.DataFrame(columns = ["Subgraph_Filename", "UniprotKB", "EC"])

    for filename in os.listdir(subgraph_dir):
        file_path = os.path.join(subgraph_dir, filename)

        df = pd.read_csv(file_path, sep = "|")
        uniprot = df[df['O_ID'].str.contains("UniprotKB:", na=False)]["O_ID"].values[0]
        p = "biolink:enables"
        o = "EC:"
        new_table_name = create_subject_object_pair_table(
            conn,
            table_name = "_".join([re.sub(r'[/_]', '', uniprot),re.sub(r'[/_]', '', o)]),
            base_table_name = "edges",
            subject = re.sub(r'[/_]', '', uniprot),
            object = re.sub(r'[/_]', '', o),
            subject_prefix = "%" + uniprot + "%",
            predicate_prefix = "%" + p + "%",
            object_prefix = "%" + o + "%"
        )

        # ct = get_table_count(conn, "_".join([re.sub(r'[/_]', '', uniprot),re.sub(r'[/_]', '', o)])))
        query = (
            f"""
            SELECT * FROM '{"_".join([re.sub(r'[/_]', '', uniprot),re.sub(r'[/_]', '', o)])}';
            """
        )

        result = conn.execute(query).fetchall()
        if len(result) == 0:
            ec = "none"
        else:
            ec = result[-1]

        drop_table(conn, "_".join([re.sub(r'[/_]', '', uniprot),re.sub(r'[/_]', '', o)]))

        new_data = {
            "Subgraph_Filename" : filename,
            "UniprotKB" : uniprot,
            "EC" : ec
        }
        new_row = pd.DataFrame([new_data])
        # Concatenate to the main DataFrame
        ec_df = pd.concat([ec_df, new_row], ignore_index=True)

    ec_df.to_csv(ec_filepath, sep = "|")

if __name__ == '__main__':
    main()

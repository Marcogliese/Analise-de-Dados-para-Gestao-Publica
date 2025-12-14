import camelot
from pathlib import Path

class PDFTableExtractor:
    """
    Class for extracting tables from native PDFs (with selectable text).
    Ignores text and other information, focusing only on the tables.
    """

    def __init__(self, pdf_path):
        """
        Initialize the extractor with the PDF path.

        Args:
            pdf_path (str): Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.tables = []

    def extract_tables(self, pages='all', method='lattice'):
        """
        Extracts all tables from the PDF.

        Args:
        pages (str): Pages to process. Ex: 'all', '1', '1-3', '1,3,5'

        method (str): 'lattice' for tables with borders or 'stream' for tables without borders

        Returns:
        list: List of pandas DataFrames containing the extracted tables
        """
        print(f"Extracting tables from {self.pdf_path}...")

        try:
            # Extract tables using Camelot
            # lattice: for tables with visible grid lines
            # stream: for tables without clear borders
            tables = camelot.read_pdf(
                self.pdf_path,
                pages=pages,
                flavor=method,
                strip_text='\n'  # Remove unnecessary line breaks.
            )

            print(f"{len(tables)} table(s) found")

            # Converts to pandas DataFrames.
            self.tables = [table.df for table in tables]

            return self.tables

        except Exception as e:
            print(f"Error extracting tables.: {e}")
            return []

    def clear_tables(self):
        """
        Cleans the extracted tables by removing empty rows/columns.

        Returns:
        list: List of cleaned DataFrames
        """
        clear_tables = []

        for i, df in enumerate(self.tables):
            print(f"Clearing table {i + 1}...")

            # Remove completely empty lines.
            df = df.dropna(how='all')

            # Remove completely empty columns.
            df = df.dropna(axis=1, how='all')

            # Remove extra white space
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # Define the first line as a header if necessary.
            if len(df) > 0:
                df.columns = df.iloc[0]
                df = df[1:]
                df.reset_index(drop=True, inplace=True)

            clear_tables.append(df)

        self.tables = clear_tables
        return self.tables

    def save_tables(self, format='csv', output_folder='extracted_tables/separate_tables'):
        """
        Saves the extracted tables to files.

        Args:
            format (str): Output format: 'csv', 'excel', 'json'
            output_folder (str): Name of the folder to save the files
        """
        # Creates the output folder if it doesn't already exist.
        Path(output_folder).mkdir(exist_ok=True)

        nome_pdf = Path(self.pdf_path).stem

        for i, df in enumerate(self.tables):
            output_file = f"{output_folder}/{nome_pdf}_tabela_{i + 1}"

            try:
                if format == 'csv':
                    df.to_csv(f"{output_file}.csv", index=False, encoding='utf-8-sig')
                    print(f"Saved: {output_file}.csv")

                elif format == 'excel':
                    df.to_excel(f"{output_file}.xlsx", index=False, engine='openpyxl')
                    print(f"Saved: {output_file}.xlsx")

                elif format == 'json':
                    df.to_json(f"{output_file}.json", orient='records',
                               force_ascii=False, indent=2)
                    print(f"Saved: {output_file}.json")

            except Exception as e:
                print(f"Error saving table. {i + 1}: {e}")

    def view_tables(self, max_rows=10):
        """
            Displays the extracted tables in the console.
            Args:
                max_rows (int): Maximum number of rows to display per table
        """
        for i, df in enumerate(self.tables):
            print(f"\n{'=' * 60}")
            print(f"TABLE {i + 1} - Dimensions: {df.shape[0]} rows x {df.shape[1]} columns")
            print(f"{'=' * 60}")
            print(df.head(max_rows))
            if len(df) > max_rows:
                print(f"\n... ({len(df) - max_rows} remaining lines)")

if __name__ == "__main__":
    pdf_file = "eOuve - Limeria.pdf"

    # Create the extractor
    extractor = PDFTableExtractor(pdf_file)

    # Extract tables
    tabelas = extractor.extract_tables(pages='all', method='lattice')

    if len(tabelas) == 0:
        print("\nTrying with the 'stream' method...")
        tabelas = extractor.extract_tables(pages='all', method='stream')

    # Clear the tables
    if tabelas:
        extractor.clear_tables()
        extractor.view_tables(max_rows=5)
        extractor.save_tables(format='csv')
    else:
        print("\nNo tables found in the PDF..")
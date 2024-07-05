import re
import pandas as pd
from regulations_rag.document import Document
from regulations_rag.reference_checker import ReferenceChecker
from regulations_rag.reference_checker import MultiReferenceChecker
from regulations_rag.regulation_table_of_content import StandardTableOfContent


class DecisionMaking(Document):
    def __init__(self, path_to_manual_as_csv_file = "./inputs/documents/decision_making.parquet"):

        main =  self.DecisionMakingReferenceChecker()
        annex = self.AnnexSectionReferenceChecker()
        reference_checker = MultiReferenceChecker([main, annex])

        self.document_as_df = pd.read_parquet(path_to_manual_as_csv_file, engine = 'pyarrow')

        document_name = "Guidelines on Automated individual decision-making and Profiling for the purposes of Regulation 2016/679"
        super().__init__(document_name, reference_checker=reference_checker)
        if not self.check_columns():
            raise AttributeError(f"The input csv file for the DecisionMaking class does not have the correct column headings")


    def check_columns(self):
        expected_columns = ["section", "subsection", "point", "heading", "text", "section_reference"]

        actual_columns = self.document_as_df.columns.to_list()
        for column in expected_columns:
            if column not in actual_columns:
                print(f"{column} not in the DataFrame version of the DecisionMaking csv file")
                return False
        return True

    def get_text(self, section_reference, add_markdown_decorators = True, add_headings = True, section_only = True):
        text, footnotes = super().get_text_and_footnotes(section_reference, add_markdown_decorators, add_headings, section_only)
        return super()._format_text_and_footnotes(text, footnotes)

    def get_heading(self, section_reference, add_markdown_decorators = False):
        return super().get_heading(section_reference, add_markdown_decorators)

    def get_toc(self):
        return StandardTableOfContent(root_node_name = self.name, reference_checker = self.reference_checker, regulation_df = self.document_as_df)



    class DecisionMakingReferenceChecker(ReferenceChecker):
        def __init__(self):
            exclusion_list = [] 
            index_patterns = [
                r'^\b(I|II|III|IV|V|VI)\b',   
                r'^\.([A-Z])', 
                r'^\.\d+', 
            ]    
            text_pattern = r'(I|II|III|IV|V|VI)(\.([A-Z]))?(\.\d+)?'

            super().__init__(regex_list_of_indices = index_patterns, text_version = text_pattern, exclusion_list=exclusion_list)

    class AnnexSectionReferenceChecker(ReferenceChecker):
        def __init__(self):
            exclusion_list = [] #
            index_patterns = [
                r'^Annex (\d+)'
            ]
            text_pattern = r'Annex \d+'

            super().__init__(regex_list_of_indices = index_patterns, text_version = text_pattern, exclusion_list=exclusion_list)

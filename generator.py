
import os
import pandas as pd
import shutil
import math
import sys


class Document:

    def __init__(self):
        self.doc_folder = os.path.join(os.getcwd(), 'document').replace("\\", "/")
        # gather volume folder paths
        illustrations_folder = os.path.join(self.doc_folder, 'illustrations').replace("\\", "/")
        self.volume_folders = self.get_directory_list(illustrations_folder)
        # gather '.csv'
        self.book_df = pd.read_csv(r'Carre_nights_text.csv')

    # --------------------------------------------------------------------------------------------------------------
    # UTILITY METHODS
    # --------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_directory_list(dir_path):
        dir_paths = sorted(  # 'sorted()' sorts elements of the list
            [  # construct list of input images from directory through list comprehension
                os.path.join(dir_path, fname).replace("\\", "/")
                # 'os.listdir(path)' returns a list containing the names of the entries in the directory given by path
                for fname in os.listdir(dir_path)
            ]
        )
        return dir_paths

    @staticmethod
    def create_directory(f_name, f_dir):
        f_path = os.path.join(f_dir, f_name).replace("\\", "/")
        if not os.path.exists(f_path):
            os.mkdir(f_path)

    @staticmethod
    def copy_starter_text_file():
        # copy starter text file
        starter_loc = os.path.join(os.getcwd(), 'Carre_nights_starter.tex')
        text_file_loc = os.path.join(os.getcwd(), 'Carre_nights.tex')
        # remove copy if it already exists
        if os.path.exists(text_file_loc):
            os.remove(text_file_loc)
        shutil.copy(starter_loc, text_file_loc)
        return text_file_loc

    # --------------------------------------------------------------------------------------------------------------
    # MAIN GENERATOR METHOD
    # --------------------------------------------------------------------------------------------------------------

    def generate_main(self):
        main_file_loc = self.copy_starter_text_file()
        # open starter text file copy
        f = open(main_file_loc, "a+", encoding='utf-8')  # encoding='utf-8' enables French accents in '.tex' file
        # write sections content
        n1 = n2 = ''
        for i in range(len(self.volume_folders)):
            curr_volume_folder = self.volume_folders[i]
            curr_volume_name = os.path.basename(curr_volume_folder)
            image_paths = self.get_directory_list(curr_volume_folder)
            for q in range(len(image_paths)):
                if q == 0:
                    im_str = os.path.basename(image_paths[q])
                    n1 = im_str[6:10]
                elif q == (len(image_paths) - 1):
                    im_str = os.path.basename(image_paths[q])
                    n2 = im_str[6:10]
            f.writelines('\n' + '\n' + chr(92) + 'chapter{Nights ' + n1 + '-' + n2 + '}' + '\n'
                         + chr(92) + 'newpage' + '\n'
                         + chr(92) + 'subfile{sections/' + curr_volume_name + '.tex}')
        # write footer
        f.writelines('\n' + '\n' + chr(92) + 'nocite{mardrus1959mille} '
                     + '% include reference in bibliography without citing within the text' + '\n'
                     + chr(92) + 'nocite{mardrus2002book}' + '\n'
                     + chr(92) + 'bibliographystyle{ieeetran}' + '\n'
                     + chr(92) + 'bibliography{References}' + '\n'
                     + chr(92) + 'addcontentsline{toc}{chapter}{Bibliography} '
                     + '% addition of bibliography to table of content' + '\n' + '\n'
                     + chr(92) + 'end{document}')
        f.close()
        # move file to document directory
        destination_loc = os.path.join(self.doc_folder, os.path.basename(main_file_loc)).replace("\\", "/")
        shutil.move(main_file_loc, destination_loc)

    # --------------------------------------------------------------------------------------------------------------
    # SECTIONS GENERATOR METHODS
    # --------------------------------------------------------------------------------------------------------------

    def add_page(self, page_paths, text_file, page_count):
        # gather current illustration name
        curr_image_path = page_paths[page_count]
        curr_image_name = os.path.basename(curr_image_path).replace(".jpg", "")
        # match row in text_df corresponding to current illustration name
        curr_df_row = self.book_df[self.book_df['Mardrus_image'] == curr_image_name]
        if not isinstance(curr_df_row.iloc[0]['Mardrus_excerpt'], str) \
                and math.isnan(curr_df_row.iloc[0]['Mardrus_excerpt']):
            text_file.close()
            sys.exit()
        sep_index = curr_image_name.find('-')
        # extract night from illustration name
        night_text = curr_image_name[5:(sep_index - 1)]
        # extract English story name
        en_name = curr_df_row.iloc[0]['Mathers_image'][(sep_index + 2):]
        # extract French text
        fr_text = curr_df_row.iloc[0]['Mardrus_excerpt']
        # extract English text
        en_text = curr_df_row.iloc[0]['Mathers_excerpt']
        # insert all content into .tex script
        text_file.writelines(chr(92) + 'section{' + night_text + '}' + '\n'
                             + chr(92) + 'textbf{\\Large{' + en_name + '}} ' + chr(92) + chr(92) + '\n' + '\n'
                             + chr(92) + 'begin{figure}[ht]' + '\n'
                             + chr(92) + 'centering' + '\n'
                             + chr(92) + 'includegraphics[height=\\figsize]{'
                             + curr_image_path[curr_image_path.find('illustrations'):] + '}' + '\n'
                             + chr(92) + 'end{figure}' + '\n' + '\n'
                             + chr(92) + 'textit{' + chr(92) + chr(92) + '\n'
                             + '"' + fr_text + '"} ' + chr(92) + chr(92) + '\n'
                             + '—' + curr_image_name + ' ' + chr(92) + chr(92) + '~' + chr(92) + chr(92) + '\n'
                             + chr(92) + 'textit{"' + en_text + '"} ' + chr(92) + chr(92) + '\n'
                             + '—' + curr_df_row.iloc[0]['Mathers_image'] + '\n' + '\n')
        if page_count != len(page_paths) - 1:
            # add next page text
            text_file.writelines(chr(92) + 'newpage' + '\n' + '\n')
        return text_file

    def add_section(self, section_count):
        curr_volume_folder = self.volume_folders[section_count]
        curr_volume_name = os.path.basename(curr_volume_folder)
        image_paths = self.get_directory_list(curr_volume_folder)
        curr_text_file = curr_volume_name + ".tex"
        text_file_loc = os.path.join(self.doc_folder, 'sections', curr_text_file)
        f = open(text_file_loc, "w+", encoding='utf-8')  # encoding='utf-8' enables French accents in '.tex' file
        # insert header text
        f.writelines(chr(92) + 'documentclass[../Carre_nights.tex]{subfiles}' + '\n' + '\n' +
                     chr(92) + 'begin{document}' + '\n' + '\n')
        for q in range(len(image_paths)):
            f = self.add_page(image_paths, f, q)
        # insert footer text
        f.writelines(chr(92) + 'end{document}')
        f.close()

    def generate_sections(self):
        # create sections folder
        self.create_directory('sections', self.doc_folder)
        # sections iteration
        for i in range(len(self.volume_folders)):
            self.add_section(i)


if __name__ == '__main__':
    Carre_nights = Document()
    Carre_nights.generate_main()
    Carre_nights.generate_sections()

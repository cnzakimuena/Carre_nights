
import os
import pandas as pd
import math
import sys


def get_directory_list(dir_path1, dir_path2):
    dir_paths = sorted(  # 'sorted()' sorts elements of the list
        [  # construct list of input images from directory through list comprehension
            os.path.join(dir_path1, fname).replace("\\", "/")
            # 'os.listdir(path)' returns a list containing the names of the entries in the directory given by path
            for fname in os.listdir(dir_path2)
        ]
    )
    return dir_paths


def add_page(text_df, page_paths, text_file, page_count):
    # gather current illustration name
    curr_image_path = page_paths[page_count]
    curr_image_name = os.path.basename(curr_image_path).replace(".jpg", "")
    # match row in text_df corresponding to current illustration name
    curr_df_row = text_df[text_df['Mardrus_image'] == curr_image_name]
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


def add_section(repo_path, text_df, section_folders, section_count):
    curr_volume_folder = section_folders[section_count]
    curr_volume_name = os.path.basename(curr_volume_folder)
    image_paths = get_directory_list(curr_volume_folder, curr_volume_folder)
    curr_text_file = curr_volume_name + ".tex"
    text_file_loc = os.path.join(repo_path, 'sections', curr_text_file)
    # curr_text_file = "image_list_" + curr_volume_name + ".tex"
    f = open(text_file_loc, "w+", encoding='utf-8')  # encoding='utf-8' enables French accents in '.tex' file
    # insert header text
    f.writelines(chr(92) + 'documentclass[../Carre_nights.tex]{subfiles}' + '\n' + '\n' +
                 chr(92) + 'begin{document}' + '\n' + '\n')
    for q in range(len(image_paths)):
        f = add_page(text_df, image_paths, f, q)
    # insert footer text
    f.writelines(chr(92) + 'end{document}')
    f.close()


def sections_loop():
    repo_folder = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    # gather volume folder paths
    illustrations_folder = os.path.join(repo_folder, 'illustrations').replace("\\", "/")
    volume_folders = get_directory_list(illustrations_folder, illustrations_folder)
    # gather '.csv'
    book_df = pd.read_csv(r'Carre_nights_text.csv')
    # sections iteration
    for i in range(len(volume_folders)):
        add_section(repo_folder, book_df, volume_folders, i)


if __name__ == '__main__':
    sections_loop()

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog

def show_gui_dialog(args, config):
    app = tk.Tk()
    app.title("AI翻译工具")

    # 设置文件选择输入框和按钮
    file_frame = tk.Frame(app)
    file_frame.pack(padx=10, pady=10)

    tk.Label(file_frame, text="待翻译文件:").pack(side=tk.LEFT)
    file_entry = tk.Entry(file_frame, width=50)
    file_entry.pack(side=tk.LEFT, padx=10)
    tk.Button(file_frame, text="浏览...", command=lambda: choose_file(file_entry, app)).pack(side=tk.LEFT)

    # 设置模型选择下拉菜单
    model_frame = tk.Frame(app)
    model_frame.pack(padx=10, pady=10)

    tk.Label(model_frame, text="选择输出格式:").pack(side=tk.LEFT)
    model_var = tk.StringVar(app)
    model_var.set("选择输出格式")
    models = ["markdown", "pdf"]
    model_menu = tk.OptionMenu(model_frame, model_var, *models)
    model_menu.pack(side=tk.LEFT, padx=10)

    # 添加源文件语言选择和翻译目标语言选择的下拉菜单，
    lang_frame = tk.Frame(app)
    lang_frame.pack(padx=10, pady=10)
    tk.Label(lang_frame, text="选择翻译目标语言:").pack(side=tk.LEFT)
    lang_to_combobox = ttk.Combobox(lang_frame, values=["中文", "英文","日文","朝鲜语"])
    lang_to_combobox.pack(side=tk.LEFT, padx=10)

    # 添加执行按钮
    execute_frame = tk.Frame(app)
    execute_frame.pack(padx=10, pady=10)

    def execute_translation():
        args.book = file_entry.get()
        args.file_format = model_var.get()
        lang_to = lang_to_combobox.get()

        if args.book and lang_to !="" and args.file_format != "选择输出格式":
            translate_pdf(args,config,lang_to)
            messagebox.showinfo("成功", "翻译完成！")
        else:
            messagebox.showerror("错误", "请选择翻译文件和输出格式！")

    tk.Button(execute_frame, text="执行", command=execute_translation).pack(side=tk.RIGHT)

    app.mainloop()


def choose_file(file_entry,app):
    filename = filedialog.askopenfilename(title="选择文件",
                                          filetypes=(("所有文件", "*.*"), ("文本文件", "*.txt")))
    file_entry.delete(0, tk.END)
    file_entry.insert(0, filename)


def translate_pdf(args, config, target_language="中文"):

    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
    model = OpenAIModel(model=model_name, api_key=api_key)

    pdf_file_path = args.book if args.book else config['common']['book']
    file_format = args.file_format if args.file_format else config['common']['file_format']

    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator = PDFTranslator(model)
    translator.translate_pdf(pdf_file_path, file_format, target_language)

if __name__ == "__main__":
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()
    config_loader = ConfigLoader(args.config)
    config = config_loader.load_config()

    if args.gui == 'true':
        # Show GUI dialog
        show_gui_dialog(args,config)
        sys.exit(0)
    elif args.service == 'true':
        # start restful service
        from flask import Flask, request, jsonify
        app = Flask(__name__)
        @app.route('/translate', methods=['GET'])
        def translate():
            # data = request.get_json()
            #获取get请求参数
            pdf_file_path = request.args.get('pdf_file_path')
            # pdf_file_path = data['pdf_file_path']
            target_language = request.args.get('target_language')
            # target_language = data['target_language']
            file_format = request.args.get('file_format')
            # file_format = data['file_format']
            model_name = config['OpenAIModel']['model']
            api_key = config['OpenAIModel']['api_key']
            model = OpenAIModel(model=model_name, api_key=api_key)
            translator = PDFTranslator(model)
            translator.translate_pdf(pdf_file_path, file_format, target_language)
            return jsonify({'message': 'Translation completed!<a href="#">Download</a>'})
        app.run(port=8090)
    # console mode
    translate_pdf(args,config)

    
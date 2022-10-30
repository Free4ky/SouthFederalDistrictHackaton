from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import pandas as pd
import random
import json
import os

from . import UPLOAD_FOLDER
from src.predictor import predictor
from src.utils import get_text_from_website

views = Blueprint('views', __name__)


inputs_info = {}
preds_info = {}


class UploadFileForm(FlaskForm):
    file = FileField('File')
    submit = SubmitField('Проверить таблицу')


@views.route('/')
def home():
    return redirect(url_for('views.validate_input'))


@views.route('/validate_table', methods=['GET', 'POST'])
def validate_table():
    form = UploadFileForm()
    if form.validate_on_submit():
        # Save file
        file = form.file.data
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(file_path)
        # Read file
        df = pd.read_excel(file_path)[[
            'Описание компании',
            'Отрасль',
            'Подотрасль',
            'Технология (1 уровень)',
            'Технология (2 уровень)',
            'Технология (3 уровень)',
        ]]
        # Process file
        input_info = []
        pred_info = []
        from tqdm import tqdm
        for _, (description, industry, subindustry, tech1, tech2, tech3) in tqdm(df.iterrows(), total=df.shape[0]):
            input_info.append({
                'description': description,
                'industry': industry,
                'subindustry': subindustry,
                'tech1': tech1,
                'tech2': tech2,
                'tech3': tech3,
            })

            pred_info.append(predictor.validate(
                description,
                industry,
                subindustry,
                tech1,
                tech2,
                tech3,
            ))
            session['id'] = random.randint(0, 1000)
            inputs_info[session['id']] = input_info
            preds_info[session['id']] = pred_info
        return redirect(url_for('views.validate_table_result'))

    return render_template('validate_table.html', form=form)


@views.route('/validate_table_result', methods=['GET', 'POST'])
def validate_table_result():
    input_info = inputs_info[session['id']]
    pred_info = preds_info[session['id']]

    if request.method == 'GET':
        i = 0
        description = input_info[0]['description']
        industry = input_info[0]['industry']
        subindustry = input_info[0]['subindustry']
        tech1 = input_info[0]['tech1']
        tech2 = input_info[0]['tech2']
        tech3 = input_info[0]['tech3']

        pred_industries = pred_info[0]['industries']
        pred_subindustries = pred_info[0]['subindustries']
        pred_techs1 = pred_info[0]['techs1']
        pred_techs2 = pred_info[0]['techs2']
        pred_techs3 = pred_info[0]['techs3']
    elif request.method == 'POST':
        i = int(request.form.get('select'))

        description = input_info[i]['description']
        industry = input_info[i]['industry']
        subindustry = input_info[i]['subindustry']
        tech1 = input_info[i]['tech1']
        tech2 = input_info[i]['tech2']
        tech3 = input_info[i]['tech3']

        pred_industries = pred_info[i]['industries']
        pred_subindustries = pred_info[i]['subindustries']
        pred_techs1 = pred_info[i]['techs1']
        pred_techs2 = pred_info[i]['techs2']
        pred_techs3 = pred_info[i]['techs3']

    return render_template(
        'validate_table_result.html',
        selected_doc=i,
        num_docs=len(input_info),
        description=description,
        industry=industry,
        subindustry=subindustry,
        tech1=tech1,
        tech2=tech2,
        tech3=tech3,
        pred_industries=pred_industries,
        pred_subindustries=pred_subindustries,
        pred_techs1=pred_techs1,
        pred_techs2=pred_techs2,
        pred_techs3=pred_techs3,
    )


@views.route('/validate_input', methods=['GET', 'POST'])
def validate_input():
    if request.method == 'POST':
        description = request.form.get('description')
        industry = request.form.get('industry')
        subindustry = request.form.get('subindustry')
        tech1 = request.form.get('tech1')
        tech2 = request.form.get('tech2')
        tech3 = request.form.get('tech3')

        if len(description) < 10:
            flash('Описание слишком короткое', category='error')
        else:
            preds = predictor.validate(
                description,
                industry,
                subindustry,
                tech1,
                tech2,
                tech3,
            )
            session['description'] = description
            session['industry'] = industry
            session['subindustry'] = subindustry
            session['tech1'] = tech1
            session['tech2'] = tech2
            session['tech3'] = tech3

            session['pred_industries'] = preds['industries']
            session['pred_subindustries'] = preds['subindustries']
            session['pred_techs1'] = preds['techs1']
            session['pred_techs2'] = preds['techs2']
            session['pred_techs3'] = preds['techs3']

            return redirect(url_for('views.validate_input_result'))

    return render_template('validate_input.html')


@views.route('/validate_input_result')
def validate_input_result():
    return render_template(
        'validate_input_result.html',
        description=session['description'],
        industry=session['industry'],
        subindustry=session['subindustry'],
        tech1=session['tech1'],
        tech2=session['tech2'],
        tech3=session['tech3'],
        pred_industries=session['pred_industries'],
        pred_subindustries=session['pred_subindustries'],
        pred_techs1=session['pred_techs1'],
        pred_techs2=session['pred_techs2'],
        pred_techs3=session['pred_techs3'],
    )

@views.route('/check_website', methods=['GET', 'POST'])
def check_website():
    if request.method == 'POST':
        website_url = request.form.get('url')

        if len(website_url) < 3:
            flash('Ссылка слишком короткая', category='error')
        else:
            website_text = get_text_from_website(website_url)
            preds = predictor.validate(website_text)

            session['website_url'] = website_url
            session['industry'] = preds['industries'][0]
            session['subindustry'] = preds['subindustries'][0]
            session['tech1'] = preds['techs1'][0]
            session['tech2'] = preds['techs2'][0]
            session['tech3'] = preds['techs3'][0]

            return redirect(url_for('views.check_website_result'))
            

    return render_template('check_website.html')

@views.route('/check_website_result')
def check_website_result():
    return render_template(
        'check_website_result.html',
        website_url=session['website_url'],
        industry=session['industry'],
        subindustry=session['subindustry'],
        tech1=session['tech1'],
        tech2=session['tech2'],
        tech3=session['tech3'],
    )

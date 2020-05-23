import datetime
from flask import render_template, redirect, request, flash
import sqlite3
import pandas as pd
from app import app, db
from app.forms import UploadForm, DeploymentForm, CollectionForm
from app.models import Deployment, Collection


@app.route('/')
@app.route('/index')
def index():
    conn = sqlite3.connect(app.config['SQL_DB_URI'])

    deps = Deployment.query.all()

    return render_template('index.html', deployments=deps)


@app.route('/deployments')
def deployments():
    pass


@app.route('/upload_report', methods=['GET', 'POST'])
def upload_report():
    form = UploadForm()
    if form.validate_on_submit():
        data = form.file.data
        file_name = data.filename
        report_metadata = file_name.split('.')[0].split('-')
        if len(report_metadata) != 4:
            flash("[{}] is incorrect file name. Try again!".format(file_name))
            return render_template('upload_report.html', form=form)
        print("Data: {}".format(file_name))
        success = True
        if report_metadata[1] == 'Win10_CU':
            success = upload_Win10_CU(form)
        elif report_metadata[1] == 'OfficeUpdate':
            success = upload_OfficeUpdate(form)

        if success:
            flash("File uploaded successfully!")
            return redirect('/')

    # if not success or it's not submit
    return render_template('upload_report.html', form=form)


def upload_Win10_CU(form):
    """
    Processes an Excel file with Windows 10 Cumulative Update report
    :param form is a FlaskForm submitted. It should contain file, new_deployment, new_cycle
    :returns boolean success
    """
    datafile = form.file.data
    filename = datafile.filename
    file_metadata = filename.split('.')[0].split('-')
    print("Metadata: {}".format(file_metadata))
    if len(file_metadata) != 4:
        flash("[{}] is incorrect file name. Try again!".format(filename), category="error")
        return
    m_cycle_title = file_metadata[0]
    m_deployment_title = file_metadata[1]
    m_report_date, m_report_time = file_metadata[2], file_metadata[3]
    m_report_datetime = parse_datetime("{0}-{1}".format(m_report_date, m_report_time))
    # load deployment record
    conn = sqlite3.connect(app.config['SQL_DB_URI'])
    cur = conn.cursor()

    m_deployment_id = 0
    print(f"New deployment: {form.new_deployment.data}")
    if form.new_deployment.data:
        cur.execute("INSERT INTO deployment (title) VALUES (:title)", {'title': m_deployment_title})
        m_deployment_id = cur.lastrowid
        conn.commit()
    else:
        cur.execute("SELECT * FROM deployment WHERE title=:title", {"title": m_deployment_title})
        row = cur.fetchone()
        if row is None:
            flash("Win10CU deployment is not found in the DB", category="error")
            cur.close()
            return False
        print("Row: {}".format(row))
        m_deployment_id = row[0]
        conn.commit()
    # try load cycle record
    m_cycle_id = 0
    if form.new_cycle.data:
        cur.execute("INSERT INTO cycle (deployment_id, title) VALUES (:dep_id, :titlle)", {m_deployment_id, m_cycle_title})
        m_cycle_id = cur.lastrowid
        conn.commit()
    else:
        cur.execute(f"SELECT * FROM cycle WHERE deployment_id={m_deployment_id} AND title='{m_cycle_title}'")
        row = cur.fetchone()
        if row is None:
            flash(f"{m_deployment_title} deployment has no [{m_cycle_title}] cycle in the DB", category="error")
            cur.close()
            return False
        m_cycle_id = row[0]

    # if the report record exists - exit
    cur.execute(f"INSERT INTO report (cycle_id, updated) VALUES ({m_cycle_id}, '{m_report_datetime}')")
    conn.commit()
    m_report_id = cur.lastrowid
    if m_report_id is None:
        flash("Report hasn't been created. Probably it already exists.")
        cur.close()
        return False
    cur.close()

    report_df = pd.read_excel(datafile, sheet_name="Sheet2", header=9, usecols="A,C,F,G,I,J,K,M,O")
    report_df.rename(columns={
        'Computer Name': 'device', 'Collection Name': 'collection',
        'OS Build Number': 'os_build_number', 'Active': 'active',
        'Last Logon': 'last_logon', 'Last Logon User': 'last_logon_user',
        'Installation Status': 'status', 'Note': 'note', 'Error Code': 'error_code'
    }, inplace=True)
    report_df['report_id'] = m_report_id
    report_df.to_sql("machine_status", con=conn, if_exists="append")
    conn.commit()
    # make sure we have all the collections in the DB
    collections_df = pd.read_sql(con=conn, sql=f"SELECT title AS collection, ring FROM collection WHERE cycle_id={m_cycle_id}")
    collections_df.set_index('collection', inplace=True)
    print(f"Collections: {collections_df.head()}")
    report_df.join(other=collections_df, on='collection')
    print(report_df[['collection', 'ring']].head())

    #collections_df = pd.DataFrame(report_df['collection'].unique()).rename(columns={0: 'title'})
    #collections_df['cycle_id'] = m_cycle_id
    #collections_df.to_sql(con=conn, name='collection', index=False, if_exists="append")
    #conn.commit()
    flash("File {} has been uploaded successfully!".format(filename))

    return True


def upload_officeupdate(datafile):
    """
    Processes an Excel file with Windows 10 Cumulative Update report
    :param datafile is a FlaskForm FileField uploaded
    :return boolean success
    """
    flash("OfficeUpdate function is not yet defined", category="error")
    return False


def parse_datetime(str_datetime):
    """
    Takes a string like 200501-1305KZN and converts it into datetime
    :param str_datetime: string representation like '200501-1305KZN'
    :return: datetime
    """

    date_parts = str_datetime.split("-")
    yy = date_parts[0][:2]
    MM = date_parts[0][2:4]
    dd = date_parts[0][-2:]
    hh = date_parts[1][:2]
    mm = date_parts[1][2:4]
    the_datetime = datetime.datetime(2000 + int(yy), int(MM), int(dd), int(hh), int(mm))

    return the_datetime


@app.route('/show_report/<int:report_id>')
def show_report(report_id):
    conn = sqlite3.connect(app.config['SQL_DB_URI'])
    cur = conn.cursor()
    report_df = pd.read_sql(con=conn, sql="SELECT * FROM ")


@app.route('/deployment/<int:deployment_id>', methods=['GET', 'POST'])
def edit_deployment(deployment_id):
    # if it's GET, then load form from DB
    if request.method == 'GET':
        depl = Deployment.query.get(deployment_id)
        form = DeploymentForm(obj=depl)

    # if it's POST, then save form to DB
    else:
        form = DeploymentForm()
        depl = Deployment.query.get(deployment_id)
        depl.title = form.title.data
        #depl.update()
        db.session.commit()
        flash("Deployment record updated")

    return render_template('edit_deployment.html', form=form)

@app.route('/collection/<int:collection_id>', methods=['GET', 'POST'])
def edit_collection(collection_id):
    if request.method == 'GET':
        collection = Collection.query.get(collection_id)
        form = CollectionForm(obj=collection)
    else:
        form = CollectionForm()
        collection = Collection.query.get(collection_id)
        collection.title = form.title.data
        collection.ring = form.ring.data
        db.session.commit()
        flash("Collection record updated")
        return redirect('/index')

    return render_template('edit_collection.html', form=form)



def GetFileList(BUCKET_NAME):
    # get file list from bucket
    bucket = s3.Bucket(BUCKET_NAME)
    objs = [obj for obj in bucket.objects.all()]
    files = [obj.key for obj in objs]
    print("Bucket name: %s \nfile list: %s" %(BUCKET_NAME, files))
    return files

def UploadFile(directory, KEY, BUCKET_NAME):
    try: 
        if directory: os.chdir(directory)
        else: directory = os.popen('pwd').read().rstrip() + '/'

        filenames = [os.path.basename(x) for x in glob.glob(str(directory) + '*{}'.format(KEY))]
        for f in filenames:
            client.upload_file(directory+f, BUCKET_NAME, f)
            print("Uploading file successed!")
            print('File name: %s, Bucket name: %s' %(f,BUCKET_NAME))
    except botocore.exceptions.ClientError as e:
              print("Uploading file FAILED!\nERROR Message:", e)

def DownloadFile(directory, KEY, BUCKET_NAME, FILE_NAME):
    if directory: os.chdir(directory)
    else: directory = os.popen('pwd').read().rstrip() + '/'

    try:
        s3.Bucket(BUCKET_NAME).download_file(KEY, FILE_NAME)
        print("File downloaded")
        print("File: %s" %(directory+FILE_NAME))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

def CreateJob():
    global S3_REGION, JOB_BUCKET_NAME, JOBID, TARGET, JOB_DOC
    try:
        createJob_response = iot.create_job(
            jobId=JOBID,
            targets=[TARGET],
            documentSource='https://'+JOB_BUCKET_NAME+'.s3.'+S3_REGION+'.amazonaws.com/'+JOB_DOC,
            description=' ',
            presignedUrlConfig={},
            targetSelection='SNAPSHOT',
            jobExecutionsRolloutConfig={},
            documentParameters={})
        # Job document and job document source cannot be specified at the same time.

        # get the job and job document information
        info_job = iot.describe_job(jobId=JOBID) # job info
        info_job_doc = iot.get_job_document(jobId=JOBID)
        job_doc_dict = ast.literal_eval(info_job_doc['document']) # job doc info

        print("New Job is created!")
        print("===========================================================================")
        print("Job name: %s" %JOBID)
        print("Target: %s" %TARGET)
        print("Status: %s" %info_job['job']['status'])
        print("Document Sourse: \n%s" %info_job['documentSource'])
        print("Document:")
        print(job_doc_dict)
        print("Responses:")
        print(createJob_response)
        print()
        return info_job, job_doc_dict
              
    except botocore.exceptions.ClientError as e:
              print("Creating job FAILED!\nERROR Message:", e)

def DeleteJob(JOBID):
    try:
        iot.delete_job(jobId=JOBID,force=True)
        print("Job has been deleted!")
        print("Job name: %s" %JOBID)
    except botocore.exceptions.ClientError as e:
              print("Cannot delete job!\nERROR Message:", e)
            

def VersionUpdate(directory, CURR_IMG_FILE):
    if directory: os.chdir(directory)
    else: directory = os.popen('pwd').read().rstrip() + '/' +

    filenames = [os.path.basename(x) for x in glob.glob(str(directory) + '*{}'.format(CURR_IMG_FILE))]
    curr_version = filenames[0].split('.')[:]
    NEW_ver = int(info_job_doc['firmware']['version'])
    CURR_ver = int(curr_version[0][-2:])
    print("New Version: %d" %NEW_ver)
    print("Current Version: %d" %CURR_ver)
    print()
    
    if NEW_ver > CURR_ver : 
        print("New Version available!")
        DownloadFile(directory, IMG_KEY, IMG_BUCKET_NAME, 'rasp_img_{}.txt'.format(NEW_ver))
        print("Updating Version ...")
        print("=======================")
        while info_job['job']['status'] == 'IN_PROGRESS':
            print(info_job['job']['status']+'...')
            time.sleep(10)
        print()
        print("Updating Statue: %s" %info_job['job']['status'])
        print()
    else: print("Latest Version!")

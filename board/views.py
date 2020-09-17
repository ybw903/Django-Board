import os

from django.shortcuts import render, redirect
from board.models import Board, Comment
from django.views.decorators.csrf import csrf_exempt


UPLOAD_DIR = 'c:/upload/'

def list(request):
    boardList = Board.objects.order_by('-idx')
    boardCount = Board.objects.count()
    return render(request,'list.html',{'boardList':boardList, 'boardCount':boardCount})

def write(request):
    return  render(request,'write.html')

@csrf_exempt
def insert(request):
    fname=''
    fsize =0
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file._name
        with open('%s%s' % (UPLOAD_DIR,fname),'wb') as fp:
            for chunck in file.chuncks():
                fp.write(chunck)
        fsize = os.path.getsize(UPLOAD_DIR + fname)
    row = Board(writer=request.POST['writer'], title=request.POST['title'], content = request.POST['content'],
                filename=fname, filesize=fsize)
    row.save()
    return redirect('/')

def detail(request):
    id = request.GET['idx']
    row = Board.objects.get(idx=id)
    row.hit_up()
    row.save()
    filesize = '%.2f'%(row.filesize/1024)
    return render(request, 'detail.html',{'row':row, 'filesize':filesize})

@csrf_exempt
def update(request):
    id = request.POST['idx']
    row_src= Board.objects.get(idx=id)
    fname = row_src.filename
    fsize = row_src.filesize
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file._name
        with open('%s%s' %(UPLOAD_DIR, fname),'wb')as fp:
            for chunck in file.chuncks():
                fp.write(chunck)
        fsize = os.path.getsize(UPLOAD_DIR+fname)
    row_new= Board(idx=id, writer=request.POST['writer'], title=request.POST['title'], content=request.POST['content'],
                   filename=fname, filesize=fsize)
    row_new.save()
    return redirect('/')

@csrf_exempt
def delete(request):
    id = request.POST['idx']
    Board.objects.get(idx=id).delete()
    return redirect('/')

from django.utils.http import urlquote
from django.http import HttpResponse, HttpResponseRedirect


def download(request):
    id = request.GET['idx']
    row = Board.objects.get(idx=id)
    path = UPLOAD_DIR +row.filename
    filenmae = os.path.basename(path) # 디렉토리를 제외한 파일 이름
    filenmae = urlquote(filenmae) # 한글/특수문자 인코딩 처리
    with open(path, 'rb') as file:
        # 서버의 파일을 읽음, content_type 파일의 종류
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition']=\
        "attachment; filename*=UTF-8''{0}".format(filenmae) # 첨부파일정보
        row.down_up()
        row.save()
        return response
def reply_insert(request):
    id = request.POST['idx']
    row = Comment(board_idx= id, writer=request.POST['writer'],content=request.POST['content'])
    print("hi")
    row.save()
    return HttpResponseRedirect('detail?idx='+id)
# Create your views here.

from flask import Flask, request, jsonify, send_from_directory
import secrets,time,threading,math
app=Flask(__name__); rooms={}; lock=threading.Lock()
@app.get('/')
def index(): return send_from_directory('.', 'index.html')
@app.post('/api/rooms')
def create():
 with lock:
  key=secrets.token_urlsafe(24); rooms[key]=dict(position=0,playing=False,updated=time.time(),revision=0)
 return jsonify(room=key)
@app.route('/api/rooms/<key>',methods=['GET','POST'])
def state(key):
 with lock:
  s=rooms.get(key)
  if s is None: return jsonify(error='Room not found'),404
  now=time.time()
  if request.method=='POST':
   d=request.get_json(silent=True) or {}; action=d.get('action'); pos=d.get('position')
   if action not in ('play','pause','seek') or type(pos) not in (int,float) or not math.isfinite(pos) or not 0<=pos<=86400: return jsonify(error='Invalid command'),400
   s.update(position=pos,updated=now,revision=s['revision']+1)
   if action!='seek': s['playing']=action=='play'
  return jsonify(**s,serverTime=now)

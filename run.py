from flaskblog import app,manager


if __name__=='__main__':
    #manager.run()
    #print('hello world')
    #print('in test branch')
    app.run(host='0.0.0.0',port=80,debug=True)

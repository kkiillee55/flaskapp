from flaskblog import app,manager


if __name__=='__main__':
    #manager.run()
    #print('hello world')
    #print('in test branch')
    app.run(port=5000,debug=True)
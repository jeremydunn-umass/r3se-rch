def test_file_creation():
    with open('testfile.txt', 'w+') as f:
        f.write('test')
        
test_file_creation()
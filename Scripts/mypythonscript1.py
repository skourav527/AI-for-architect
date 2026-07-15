# print("hello worls")
# mystring = 'shivkumar'
# print (mystring.upper())
# print('this is {} {} {}'.format('shiv','kumar','kourav'))
# mylist= [4,3,6,5,9]
# mylist[0] = 'shiv'
# mylist.append('kumar')
# mylist.pop(5)
# # mylist.sort()
# print(mylist)
# my_discnory = {'key1':[1,2,3],'key2':200,'key3':400}
# print(my_discnory['key1'][1])

with open('myfile.txt', 'w') as f:
    f.write('Hello World')

with open('myfile.txt', 'r') as f:
    content = f.read()
    print(content)
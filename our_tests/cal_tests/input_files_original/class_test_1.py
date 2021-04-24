class myClass():
    x = 1

    class myClass1(Parent1):
        y = 1

        class myClass2(Parent1):
            z = 1

    class myClass3(Parent1):
        a = 1

class myClass4(Parent1, Parent1):
    b = 1
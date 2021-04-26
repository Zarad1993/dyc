class MyClass:
    """
    MyClass Description
    """

    x = 1

    class MyClass1(Parent1):
        """
        MyClass1 Description

        Inheritance
        -----------
        Parent1: Parent1 Description
        """

        y = 1

        class MyClass2(Parent1, Parent2):
            """
            MyClass2 Description

            Inheritance
            -----------
            Parent1: Parent1 Description
            Parent2: Parent2 Description
            """

            z = 1

    class MyClass3(Parent1):
        """
        MyClass3 Description

        Inheritance
        -----------
        Parent1: Parent1 Description
        """

        a = 1


class MyClass4(Parent1, Parent2):
    """
    MyClass4 Description

    Inheritance
    -----------
    Parent1: Parent1 Description
    Parent2: Parent2 Description
    """

    b = 1

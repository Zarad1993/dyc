class myClass():
    """
    This is myClass

    Inheritance
    -----------

    """
    x = 1

    class myClass1(Parent1):
        """
        This is myClass1

        Inheritance
        -----------
        
        """
        y = 1

        class myClass2(Parent1):
            """
            Test
            """
            z = 1

    class myClass3(Parent1):
        """
        This is myClass3

        Inheritance
        -----------
        
        """
        a = 1

class myClass4(Parent1, Parent1):
    """
    This is myClass4

    Inheritance
    -----------
    
    """
    b = 1
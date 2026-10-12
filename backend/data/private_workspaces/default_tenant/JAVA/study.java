import java.util.Scanner;
public class Main{
    public static void main(String[] args){
        double width,height;
        Scanner sc=new Scanner(System.in);
        System.out.print("Enter the width of rectangle: ");
        width=sc.nextDouble();
        System.out.print("Enter the height of rectangle: ");
        height=sc.nextDouble();
        System.out.println("Area of rectangle is:"+width*height);
        sc.close();
    }
}
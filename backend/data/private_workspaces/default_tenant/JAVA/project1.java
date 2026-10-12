import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

public class project1 {
    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);

        System.out.print("Enter participant name: ");
        String name = sc.nextLine();

        System.out.print("Enter course name: ");
        String course = sc.nextLine();

        System.out.print("Enter date: ");
        String date = sc.nextLine();

        System.out.print("Enter certificate ID: ");
        String id = sc.nextLine();

        try {
            FileWriter file = new FileWriter("certificate.txt");

            file.write("========================================\n");
            file.write("          DIGITAL CERTIFICATE\n");
            file.write("========================================\n\n");

            file.write("Certificate ID: " + id + "\n\n");

            file.write("This is to certify that\n\n");
            file.write("             " + name + "\n\n");

            file.write("has successfully completed the course\n\n");
            file.write("             " + course + "\n\n");

            file.write("Date: " + date + "\n\n");

            file.write("        Congratulations!\n");

            file.write("\n========================================\n");

            file.close();

            System.out.println("\nCertificate generated successfully!");
            System.out.println("File: certificate.txt");

        } catch (IOException e) {
            System.out.println("Error while creating certificate.");
        }

        sc.close();
    }
}
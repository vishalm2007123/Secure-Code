public class ConcatTest {
    public static void main(String[] args) {

        long startTime = System.currentTimeMillis();

        StringBuffer sb = new StringBuffer("java");

        for (int i = 0; i < 1000; i++) {
            sb.append("point");
        }

        System.out.println("Time taken: "
                + (System.currentTimeMillis() - startTime) + " ms");

        startTime = System.currentTimeMillis();

        StringBuilder sb2 = new StringBuilder("java");

        for (int i = 0; i < 1000; i++) {
            sb2.append("gahs");
        }

        System.out.println("Time taken: "
                + (System.currentTimeMillis() - startTime) + " ms");
    }
}
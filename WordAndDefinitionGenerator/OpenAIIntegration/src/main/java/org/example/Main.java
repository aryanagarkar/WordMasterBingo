package org.example;

import java.io.*;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

// TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {
        String filePath = "WordsToProcess.txt";
        String outputFile = "WordDefinitionsAndSynonyms.txt";

        BufferedWriter writer = null;
        BufferedReader reader = null;

        List<String> wordsList = new ArrayList<>();

        try {
            reader = new BufferedReader(
                    new InputStreamReader(Main.class.getClassLoader().getResourceAsStream(filePath)));
            writer = new BufferedWriter(new FileWriter(outputFile, true));

            String line;
            while ((line = reader.readLine()) != null) {
                wordsList.add(line.trim());
            }

            Collections.shuffle(wordsList);
            System.out.println("Size: " + wordsList.size());

            int i = 0;
            for (String s : wordsList) {
                String response = MeaningAndSynonymFetcher.getDefinitions(s);
                System.out.println(i++ + " " + s);
                writer.write(i + ". " + s + ": " + response + "\n");
            }
            writer.close();

        } catch (Exception e) {
            System.out.println("There was an error: " + e);
        }

    }
}
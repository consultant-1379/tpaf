package com.ericsson.procus.tpaf.installer;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import javafx.scene.Scene;
import javafx.scene.effect.Reflection;
import javafx.scene.layout.BorderPane;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.scene.text.Text;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

import com.ericsson.procus.tpaf.utils.TPAFenvironment;


public class TPAFenvInstaller {
	
	private Stage stage;
	
	public boolean isRequired(){
		boolean required = true;
		File envbase = new File(TPAFenvironment.ENVBASEDIR);
		if(envbase.exists()){
			File envRState = new File(envbase, "TPAFenv.txt");
			if(envRState.exists()){
				try {
					String content = readFile(envRState.getAbsolutePath(), Charset.defaultCharset());
					content = content.split("=")[1];
					if(content.equalsIgnoreCase(TPAFenvironment.PRODUCTRSTATE)){
						required = false;
					}
				} catch (IOException e) {}
			}
		}
		return required;
		
	}
	
	public void installEnvironment(){
		
		File libsDir = new File(".\\libs");
		if(!libsDir.exists()){
			libsDir = new File(".\\resources");
		}
		
		File envBase = new File(TPAFenvironment.ENVBASEDIR);
		envBase.mkdirs();
		unZipIt(libsDir.getAbsolutePath()+"\\resources.jar",envBase.getAbsolutePath());
		
		writeRstateFile(envBase.getAbsolutePath());
		
		closeStage();
		
	}
	
	public void showStage(){
		stage = new Stage(StageStyle.UNDECORATED);
		
		BorderPane base = new BorderPane();
        
		base.setStyle("-fx-background-color:linear-gradient(WHITESMOKE 65%, silver 20%);");
		
		Text text = new Text(20, 110, "Installing TP AF Environemnt");
        text.setFill(Color.DODGERBLUE);
        text.setFont(Font.font(Font.getDefault().getFamily(), 35));
        
        Reflection r = new Reflection();
        r.setFraction(0.9f);
         
        text.setEffect(r);
		
		base.setCenter(text);
		
		Scene scene = new Scene(base, 600, 150, Color.WHITESMOKE);
        stage.setScene(scene);
        stage.centerOnScreen();
        stage.toFront();
        stage.show();
	}
	
	private void closeStage(){
		stage.close();
	}
	
	
	private String readFile(String path, Charset encoding) throws IOException {
		byte[] encoded = Files.readAllBytes(Paths.get(path));
		return encoding.decode(ByteBuffer.wrap(encoded)).toString();
	}
	
	private void writeRstateFile(String envbase){
		try {
			PrintWriter out = new PrintWriter(envbase+"\\TPAFenv.txt");
			out.print("InstalledVersion="+TPAFenvironment.PRODUCTRSTATE);
			out.flush();
			out.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	private void unZipIt(String zipFile, String outputFolder){
	     byte[] buffer = new byte[1024];
	     try{

	    	File folder = new File(outputFolder);
	    	if(!folder.exists()){
	    		folder.mkdir();
	    	}

	    	ZipInputStream zis = new ZipInputStream(new FileInputStream(zipFile));
	    	ZipEntry ze = zis.getNextEntry();
	 
			while (ze != null) {

				String fileName = ze.getName();
				if (fileName.contains(".")) {
					File newFile = new File(outputFolder + File.separator+ fileName);

					new File(newFile.getParent()).mkdirs();

					FileOutputStream fos = new FileOutputStream(newFile);

					int len;
					while ((len = zis.read(buffer)) > 0) {
						fos.write(buffer, 0, len);
					}
					fos.close();
				}
				ze = zis.getNextEntry();
			}
	        zis.closeEntry();
	    	zis.close();	 
	    }catch(IOException ex){
	       ex.printStackTrace(); 
	    }
	   }

}

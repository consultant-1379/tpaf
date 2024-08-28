package com.ericsson.procus.tpaf;

import java.io.FileOutputStream;
import java.io.PrintStream;

import com.ericsson.procus.tpaf.controller.Controller;
import com.ericsson.procus.tpaf.controller.IntroController;
import com.ericsson.procus.tpaf.controller.jobs.JobScheduler;
import com.ericsson.procus.tpaf.installer.TPAFenvInstaller;
import com.ericsson.procus.tpaf.model.ModelFactory;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;

import javafx.application.Application;
import javafx.event.EventHandler;
import javafx.scene.image.Image;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;

public class TPAFmain extends Application {

	@Override
	public void start(Stage primaryStage) {
		
		TPAFenvInstaller installer = new TPAFenvInstaller();
		if(installer.isRequired()){
			installer.showStage();
			installer.installEnvironment();
		}
		
//		try{
//			PrintStream out = new PrintStream(new FileOutputStream(TPAFenvironment.OUTPUTDIR+"\\output.txt"));
//			System.setOut(out);
//		}catch(Exception e){
//			e.printStackTrace();
//		}
		
		
		//Create model python loader
		ModelFactory modelcreator = new ModelFactory();
		
		View view = new View(primaryStage);
		
		//Create entry controller
		Controller startController = new IntroController(modelcreator, view);
		startController.execute();
		
		primaryStage.setOnCloseRequest(new EventHandler<WindowEvent>() {
			public void handle(WindowEvent e) {
				JobScheduler.getInstance().shutdown();
				System.exit(0);
			}
		});
		
		primaryStage.getIcons().add(new Image("file:TPAF.bmp"));
		primaryStage.show();
	}

	public static void main(String[] args) {
		launch(args);
	}
}

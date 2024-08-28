package com.ericsson.procus.tpaf.view.elements;

import java.util.ArrayList;

import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ListView;
import javafx.scene.control.RadioButton;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.ToggleGroup;
import javafx.scene.control.ScrollPane.ScrollBarPolicy;
import javafx.scene.control.Separator;
import javafx.scene.control.Tab;
import javafx.scene.control.TextField;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.ColumnConstraints;
import javafx.scene.layout.ColumnConstraintsBuilder;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;

import com.ericsson.procus.tpaf.controller.Controller;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;

public class IntroView {

	private Controller listener;
	
	public void setListener(Controller listener){
		this.listener = listener;
	}
	
	public Node getTitleBar(String username){
		BorderPane titleBar = new BorderPane();
		titleBar.getStyleClass().add(TPAFenvironment.TITLEBAR_BACKGROUND);
		
		Text title = new Text(TPAFenvironment.PRODUCTNAME + " " + TPAFenvironment.PRODUCTRSTATE);
		title.getStyleClass().addAll(TPAFenvironment.WHITEFONT, TPAFenvironment.LARGEFONT);
		
		Text userName = new Text(username);
		userName.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
		
		titleBar.setLeft(title);
		titleBar.setRight(userName);
		BorderPane.setMargin(title, new Insets(0, 0, 0, 10));
		BorderPane.setMargin(userName, new Insets(0, 10, 0, 0));
		return titleBar;
	}
	
	public Node getIntroPane(){	
		Text title = new Text("Welcome to the Tech Pack Automation Framework (TP AF)");
		title.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.XLFONT);
		
		Text instructions = new Text("Please verify your SIGNUM below and select an input to begin.");
		instructions.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.LARGEFONT);
		
		Text signumText = new Text("SIGNUM: ");
		signumText.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.LARGEFONT);
		
		Text signum = new Text(TPAFenvironment.USERNAME);
		signum.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.LARGEFONT);
		
		HBox signumBox = new HBox();
		signumBox.getChildren().addAll(signumText, signum);
		signumBox.setAlignment(Pos.CENTER);
		signumBox.setPadding(new Insets(100, 0, 0, 0));
		signumBox.setSpacing(10);
		
		GridPane optionsGrid = new GridPane();
		optionsGrid.setId("options");
		optionsGrid.setPadding(new Insets(50, 20, 10, 20));
		optionsGrid.setHgap(20);
		
		Button xml = new Button("Load from a TP AF XML file");
		xml.setWrapText(true);
	    xml.setId("loadOption");
	    xml.setPrefSize(500, 700);
	    xml.getStyleClass().addAll(TPAFenvironment.XMLLOAD, TPAFenvironment.XLFONT);
	    xml.setOnAction(listener);
		
		Button fd = new Button("Load from a Function Description");
		fd.setWrapText(true);
		fd.setId("loadOption");
		fd.setPrefSize(500, 700);
		fd.getStyleClass().addAll(TPAFenvironment.FDLOAD, TPAFenvironment.XLFONT);
		fd.setOnAction(listener);
	    
	    Button server = new Button("Load from a server");
	    server.setWrapText(true);
	    server.setId("loadOption");
	    server.setPrefSize(500, 700);
	    server.getStyleClass().addAll(TPAFenvironment.SERVERLOAD, TPAFenvironment.XLFONT);
	    server.setOnAction(listener);
	    
	    Button tpi = new Button("Load from a tpi file");
	    tpi.setWrapText(true);
	    tpi.setId("loadOption");
	    tpi.setPrefSize(500, 700);
	    tpi.getStyleClass().addAll(TPAFenvironment.TPILOAD, TPAFenvironment.XLFONT);
	    tpi.setOnAction(listener);
	    
	    optionsGrid.getChildren().addAll(fd, server, tpi, xml);
	    GridPane.setConstraints(xml, 0, 0);
	    GridPane.setConstraints(fd, 1, 0);
	    GridPane.setConstraints(server, 2, 0);
	    GridPane.setConstraints(tpi, 3, 0);
	    
	    ColumnConstraints widthconstraint = ColumnConstraintsBuilder.create().percentWidth(25).build();
	    optionsGrid.getColumnConstraints().addAll(widthconstraint, widthconstraint,widthconstraint);
		
		VBox introPane = new VBox();
		introPane.setId("BaseVBox");
		introPane.getChildren().addAll(title, instructions, signumBox, optionsGrid);
		introPane.setAlignment(Pos.TOP_CENTER);
		introPane.setPadding(new Insets(20, 0, 0, 0));
		introPane.setSpacing(20);
				
		return introPane;
	}

	
	public void getFDLoadOptions(VBox base, String style){
		GridPane grid = (GridPane)base.getChildren().get(base.getChildren().size()-1);
		double width = grid.getWidth();
		double height = grid.getHeight();
		base.getChildren().remove(base.getChildren().size()-1);
		
		StackPane pane = new StackPane();
		Rectangle fd = new Rectangle(width-40, height-70);
		fd.setArcHeight(25);
		fd.setArcWidth(25);
		fd.getStyleClass().add(style);
		
		BorderPane entries = new BorderPane();
		HBox topSection = new HBox();
		Text back = new Text("<Back");
		back.setId("back");
		back.getStyleClass().addAll(TPAFenvironment.WHITEFONT, TPAFenvironment.LARGEFONT);
		back.setOnMouseClicked(listener);
	    topSection.getChildren().add(back);
	    entries.setTop(topSection);
	    
	    if(!style.equalsIgnoreCase(TPAFenvironment.SERVERLOAD)){
	    	entries.setCenter(drawFileLoadOptions(style));
	    }else{
	    	entries.setCenter(drawServerLoadOptions(style));
	    }
	    	
    	HBox bottomSection = new HBox();
 		Text Load = new Text("Load");
 		Load.setId("Load");
 		Load.getStyleClass().addAll(TPAFenvironment.WHITEFONT, TPAFenvironment.XLFONT);
 		Load.setOnMouseClicked(listener);
 		
 		bottomSection.getChildren().add(Load);
 		bottomSection.setAlignment(Pos.BOTTOM_RIGHT);
 		bottomSection.setPadding(new Insets(0, 20, 0, 0));
 	    entries.setBottom(bottomSection);
    
		pane.getChildren().addAll(fd,entries);
		pane.setPadding(new Insets(50, 20, 10, 20));
		base.getChildren().addAll(pane);
	}
	
	private Node drawServerLoadOptions(String option){
		VBox base = new VBox();
		base.setSpacing(10);
		
		HBox input = new HBox();
		input.setSpacing(10);
		
		TextField inputLocation = new TextField();
		inputLocation.setPrefColumnCount(30);
		inputLocation.setId("input");
		inputLocation.setPrefHeight(40);
		inputLocation.setPromptText("Enter server name or IP address");
		
		final Text browse = new Text("Get TP's");
		browse.setId(option);
		browse.getStyleClass().addAll(TPAFenvironment.WHITEFONT, TPAFenvironment.XLFONT);
		browse.setOnMouseClicked(listener);		
		
		input.getChildren().addAll(inputLocation, browse);
		input.setAlignment(Pos.CENTER);
		
		HBox stack = new HBox();
		stack.setId("ServerLoadBase");
		stack.setAlignment(Pos.CENTER);
		
		base.getChildren().addAll(input, stack);
		base.setAlignment(Pos.TOP_CENTER);
		
		//Set the focus onto "Browse" so the prompt text will be visible in the TextField
		Platform.runLater(new Runnable() {
		     @Override
		     public void run() {
		    	 browse.requestFocus();
		     }
		});

		return base;
	}
	
	public void addWaitMessage(final HBox pane){
		Platform.runLater(new Runnable() {
		     @Override
		     public void run() {
		    	final Text wait = new Text("This may take a moment");
		 		wait.getStyleClass().addAll(TPAFenvironment.WHITEFONT, TPAFenvironment.XLFONT);
		 		pane.getChildren().clear();
		 		pane.getChildren().addAll(wait);
		     }
		});
	}
	
	private Node drawFileLoadOptions(String option){
		HBox input = new HBox();
		input.setSpacing(10);
		
		TextField inputLocation = new TextField();
		inputLocation.setPrefColumnCount(60);
		inputLocation.setId("input");
		inputLocation.setPrefHeight(40);
		if(option.equalsIgnoreCase(TPAFenvironment.FDLOAD)){
			inputLocation.setPromptText("Enter Function Description location...");
		}else if(option.equalsIgnoreCase(TPAFenvironment.TPILOAD)){
			inputLocation.setPromptText("Enter tpi file location...");
		}else if(option.equalsIgnoreCase(TPAFenvironment.XMLLOAD)){
			inputLocation.setPromptText("Enter XML file location...");
		}
		
		final Text browse = new Text("Browse...");
		browse.setId(option);
		browse.getStyleClass().addAll(TPAFenvironment.WHITEFONT, TPAFenvironment.XLFONT);
		browse.setOnMouseClicked(listener);		
		
		input.getChildren().addAll(inputLocation, browse);
		input.setAlignment(Pos.CENTER);
		
		//Set the focus onto "Browse" so the prompt text will be visible in the TextField
		Platform.runLater(new Runnable() {
		     @Override
		     public void run() {
		    	 browse.requestFocus();
		     }
		});
		return input;
	}
	
	public void showTPfromServer(final HBox node, final ArrayList<String> listofNames){
		
		Platform.runLater(new Runnable() {
			@Override
			public void run() {
				node.getChildren().clear();
				
				ToggleGroup radioGroup = new ToggleGroup();
				
				VBox col1 = new VBox();
				col1.setId("ServerLoadRadioCol");
				col1.setSpacing(20);
				
				VBox col2 = new VBox();
				col2.setSpacing(20);
				
				VBox col3 = new VBox();
				col3.setSpacing(20);
				
				int count = 0;
				for(String name : listofNames){
					RadioButton tpName = new RadioButton(name.replace("_", " "));
					tpName.getStyleClass().addAll(TPAFenvironment.WHITEFONT, TPAFenvironment.LARGEFONT);
					tpName.setToggleGroup(radioGroup);
					tpName.setOnAction(listener);
					
					if(count % 3 == 0){
						col1.getChildren().addAll(tpName);
					}else if(count % 3 == 1){
						col2.getChildren().addAll(tpName);
					}else{
						col3.getChildren().addAll(tpName);
					}
					count = count + 1;
				}
				
				HBox base = new HBox();
				base.setSpacing(10);
				base.getChildren().addAll(col1, col2, col3);
				
				ScrollPane scrollpane = new ScrollPane();
				scrollpane.getStyleClass().add(TPAFenvironment.FDLOAD);
				scrollpane.setPrefViewportHeight(300);
				scrollpane.setPrefViewportWidth(1100);
				scrollpane.setContent(base);
				scrollpane.setHbarPolicy(ScrollBarPolicy.AS_NEEDED);
				scrollpane.setVbarPolicy(ScrollBarPolicy.AS_NEEDED);
				
				node.getChildren().add(scrollpane);
			}
		});
	}
	
	
	public Node drawTPViewPane(){
		BorderPane TPViewPane = new BorderPane();
		TPViewPane.getStyleClass().add(TPAFenvironment.BASE_BACKGROUND);
		
		return TPViewPane;
	}
	
}

package com.ericsson.procus.tpaf.view.elements.options;

import java.util.ArrayList;
import java.util.HashMap;

import javafx.application.Platform;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Dialogs;
import javafx.scene.control.RadioButton;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleGroup;
import javafx.scene.control.Dialogs.DialogOptions;
import javafx.scene.control.Dialogs.DialogResponse;
import javafx.scene.control.ScrollPane.ScrollBarPolicy;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.util.Callback;

import com.ericsson.procus.tpaf.model.ModelFactory;
import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;

public class LoadTPfromServer {

	private View view;
	private ModelFactory modelcreator;
	
	private ScrollPane scrollpane;
	private ToggleGroup radioGroup;
	private TextField inputLocation;
	
	private HashMap<String, String> results = new HashMap<String, String>();
	
	public LoadTPfromServer(View view, ModelFactory modelcreator){
		this.view = view;
		this.modelcreator = modelcreator;
	}
	
	
	public HashMap<String, String> showLoadingWindow(){
		VBox base = new VBox();
		base.setSpacing(10);
		
		HBox input = new HBox();
		input.setSpacing(10);
		
		inputLocation = new TextField();
		inputLocation.setPrefColumnCount(25);
		inputLocation.setId("input");
		inputLocation.setPromptText("Enter server name or IP address");
		
		final Button browse = new Button("Get TP's");
		browse.getStyleClass().addAll(TPAFenvironment.WHITEFONT, TPAFenvironment.MEDIUMFONT);
		browse.setOnMouseClicked(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent event) {
                addWaitingMessage();
                
                final ArrayList<String> ListofNames = new ArrayList<String>();

				new Thread(new Runnable() {
	                public void run() {
	                	Object obj = view.lookup("#input");
	    				final String location = inputLocation.getText();
	    				modelcreator.init();
	    				ModelInterface model = modelcreator.create();
	    				ListofNames.addAll(model.getTPNameFromServer(location));
	    				showTPfromServer(ListofNames);
	                }
	            }).start();

            }
        });		
		
		input.getChildren().addAll(inputLocation, browse);
		input.setAlignment(Pos.CENTER);
		
		HBox stack = new HBox();
		stack.setAlignment(Pos.CENTER);
		
		scrollpane = new ScrollPane();
		scrollpane.getStyleClass().add(TPAFenvironment.FDLOAD);
		scrollpane.setMinSize(450, 300);
		scrollpane.setPrefViewportHeight(300);
		scrollpane.setPrefViewportWidth(450);
		scrollpane.setHbarPolicy(ScrollBarPolicy.AS_NEEDED);
		scrollpane.setVbarPolicy(ScrollBarPolicy.AS_NEEDED);
		
		stack.getChildren().add(scrollpane);
		
		
		base.getChildren().addAll(input, stack);
		base.setAlignment(Pos.TOP_CENTER);
		
		
		DialogResponse resp = Dialogs.showCustomDialog(view.getStage(), base, "Enter a server and select a TP to load", "Load from server", 
				DialogOptions.OK_CANCEL, myCallback);
		
		if(resp == DialogResponse.CANCEL){
			results.clear();
		}
		
		
		return results;
	}
	
	private void addWaitingMessage(){
		Platform.runLater(new Runnable() {
		     @Override
		     public void run() {
		    	final Text wait = new Text("This may take a moment");
		 		wait.getStyleClass().addAll(TPAFenvironment.WHITEFONT, TPAFenvironment.MEDIUMFONT);
		 		scrollpane.setContent(wait);
		     }
		});
	}
	
	
public void showTPfromServer(final ArrayList<String> listofNames){
		
		Platform.runLater(new Runnable() {
			@Override
			public void run() {
				
				radioGroup = new ToggleGroup();
				
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
				
				scrollpane.setContent(base);
			}
		});
	}
	

Callback<Void, Void> myCallback = new Callback<Void, Void>() {
	@Override
	public Void call(Void param) {
		try{
		results.put("ServerName", inputLocation.getText());
		
		RadioButton button = ((RadioButton)radioGroup.getSelectedToggle());
		String TPName = button.getText().replace(" ", "_");
		
		results.put("TPName", TPName);
		}catch(Exception e){
			//do nothing for now
		}
		
		return null;
	}
};



}

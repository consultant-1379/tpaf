package com.ericsson.procus.tpaf.view.elements;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.SortedSet;
import java.util.TreeSet;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.Accordion;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Separator;
import javafx.scene.control.Tab;
import javafx.scene.control.TextField;
import javafx.scene.control.TitledPane;
import javafx.scene.control.Tooltip;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.ColumnConstraints;
import javafx.scene.layout.ColumnConstraintsBuilder;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;

import com.ericsson.procus.tpaf.controller.Controller;
import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;

public class TpView{

	private Controller listener;
	private ModelInterface model;
	
	public TpView(ModelInterface model){
		this.model = model;
	}
	
	public void setListener(Controller listener){
		this.listener = listener;
	}
	
	public Tab drawTPviewTab(){
		Tab tpview = new Tab(model.getTechPackName());
		tpview.setId(model.getModelUID()+"_Tab");
		tpview.setClosable(true);
		
		VBox base = new VBox();
		base.setSpacing(20);
		base.setId("tpViewVBox");
		base.getStyleClass().add(TPAFenvironment.BASE_BACKGROUND);
		
		HBox titleInfo = new HBox();
		titleInfo.setAlignment(Pos.CENTER_LEFT);
		titleInfo.setPadding(new Insets(0, 10, 0, 5));
		
		VBox titlebase = new VBox();
		titlebase.setAlignment(Pos.TOP_LEFT);
		titlebase.setPadding(new Insets(0, 10, 0, 5));
		
		Text Title = new Text(model.getTechPackName());
	    Title.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.XLFONT);
	    
	    BorderPane loadbase = new BorderPane();
	    loadbase.setPadding(new Insets(0, 10, 0, 5));
	    Text source = new Text("Loaded from: " + model.getLoadSource());
	    source.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
	    
	    loadbase.setBottom(source);
	    titleInfo.getChildren().addAll(Title, loadbase);
	    titlebase.getChildren().addAll(titleInfo, new Separator());
	    
	    GridPane version = new GridPane();
	    version.setPadding(new Insets(10, 10, 10, 10));
	    version.setHgap(10);
	    version.setId("tpViewVersion");
	    version.getStyleClass().add("VersionBackground");
	    
	    ColumnConstraints widthconstraint = ColumnConstraintsBuilder.create().percentWidth(33).build();
	    version.getColumnConstraints().addAll(widthconstraint, widthconstraint, widthconstraint);
	    
	    widthconstraint = ColumnConstraintsBuilder.create().percentWidth(50).build();
	   
	    GridPane col1 = new GridPane();
	    col1.setPadding(new Insets(5, 10, 5, 10));
	    col1.setHgap(10);
	    col1.getColumnConstraints().addAll(widthconstraint);
	    
	    GridPane col2 = new GridPane();
	    col2.setPadding(new Insets(5, 10, 5, 10));
	    col2.setHgap(10);
	    col2.getColumnConstraints().addAll(widthconstraint);
	    
	    GridPane col3 = new GridPane();
	    col3.setPadding(new Insets(5, 10, 5, 10));
	    col3.setHgap(10);
	    col3.getColumnConstraints().addAll(widthconstraint);
		
		HashMap<String, String> versioning = model.getVersioningInformation();
	    Iterator it = versioning.entrySet().iterator();
	    int count = 0;
	    while (it.hasNext()) {
	        Map.Entry pairs = (Map.Entry)it.next();
	        
	        Text key = new Text(pairs.getKey().toString()+":");
	        key.setId("key");
	        key.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.MEDIUMFONT);
			
			TextField value = new TextField();
			value.setId("value");
			value.setPrefColumnCount(20);
			value.setPrefHeight(20);
			value.setText(pairs.getValue().toString());
			
			int row = 0;
			if(count % 3 == 0){
				col1.getChildren().addAll(key, value);
				row = col1.getChildren().size()/2;
			}else if(count % 3 == 1){
				col2.getChildren().addAll(key, value);
				row = col2.getChildren().size()/2;
			}else{
				col3.getChildren().addAll(key, value);
				row = col3.getChildren().size()/2;
			}
			
			GridPane.setConstraints(key, 0, row);
			GridPane.setConstraints(value, 1, row);
			
			count = count + 1;
	        it.remove(); // avoids a ConcurrentModificationException
	    }
		
		version.getChildren().addAll(col1, col2, col3);
		GridPane.setConstraints(col1, 0, 0);
		GridPane.setConstraints(col2, 1, 0);
		GridPane.setConstraints(col3, 2, 0);
		
		GridPane split = new GridPane();
		split.setPadding(new Insets(5, 10, 5, 10));
		split.setHgap(10);
		split.getColumnConstraints().addAll(widthconstraint,widthconstraint);
		
		BorderPane leftSide = new BorderPane();
		leftSide.setId(model.getModelUID()+"leftside");
		BorderPane rightSide = new BorderPane();
		rightSide.setId(model.getModelUID()+"rightside");
		split.getChildren().addAll(leftSide, rightSide);
		GridPane.setConstraints(leftSide, 0, 0);
		GridPane.setConstraints(rightSide, 1, 0);
		
	    
	    base.getChildren().addAll(titlebase, version, AddOptions(),split);
	    base.setAlignment(Pos.TOP_CENTER);
	    
	    tpview.setContent(base);
		
		return tpview;
	}
	
	private GridPane AddOptions(){
		GridPane optionsGrid = new GridPane();
		optionsGrid.setId("options");
		optionsGrid.setPadding(new Insets(5, 10, 10, 5));
		optionsGrid.setHgap(20);
		
		Button designRules = new Button("Design Rules");
		designRules.setWrapText(true);
	    designRules.setId("DesignRules");
	    designRules.setPrefSize(500, 60);
	    designRules.setMinHeight(60);
	    designRules.getStyleClass().addAll(TPAFenvironment.XMLLOAD, TPAFenvironment.LARGEFONT);
	    designRules.setOnAction(listener);
		
		Button create = new Button("Creation");
		create.setWrapText(true);
		create.setId("create");
		create.setPrefSize(500, 60);
		create.setMinHeight(60);
		create.getStyleClass().addAll(TPAFenvironment.FDLOAD, TPAFenvironment.LARGEFONT);
		create.setOnAction(listener);
	    
	    Button placeholder1 = new Button("Deletion");
	    placeholder1.setWrapText(true);
	    placeholder1.setId("delete");
	    placeholder1.setPrefSize(500, 60);
	    placeholder1.setMinHeight(60);
	    placeholder1.getStyleClass().addAll(TPAFenvironment.SERVERLOAD, TPAFenvironment.LARGEFONT);
	    placeholder1.setOnAction(listener);
	    
	    Button placeholder2 = new Button("Difference");
	    placeholder2.setWrapText(true);
	    placeholder2.setId("difference");
	    placeholder2.setPrefSize(500, 60);
	    placeholder2.setMinHeight(60);
	    placeholder2.getStyleClass().addAll(TPAFenvironment.TPILOAD, TPAFenvironment.LARGEFONT);
	    placeholder2.setOnAction(listener);
	    
	    optionsGrid.getChildren().addAll(create, placeholder1, placeholder2, designRules);
	    GridPane.setConstraints(designRules, 0, 0);
	    GridPane.setConstraints(create, 1, 0);
	    GridPane.setConstraints(placeholder1, 2, 0);
	    GridPane.setConstraints(placeholder2, 3, 0);
	    
	    ColumnConstraints widthconstraint = ColumnConstraintsBuilder.create().percentWidth(25).build();
	    optionsGrid.getColumnConstraints().addAll(widthconstraint, widthconstraint,widthconstraint);
	    
	    return optionsGrid;
	}
	
	
	public void createDRTOptions(HashMap<String, HashMap<String, String>> files, BorderPane position){		
		Accordion accordion = new Accordion();
		accordion.setId(model.getModelUID()+"DesignRulesAccordion");
		
		SortedSet<String> keys = new TreeSet<String>(files.keySet());
		for (String key : keys) {
	        
	        TitledPane tp = new TitledPane();
	        tp.setText(key);
	        VBox ruleItems = new VBox();
	        ruleItems.setId(model.getModelUID()+key+"VBox");
	        
	        CheckBox all = new CheckBox(" -> TOGGLE ALL");
	        all.getStyleClass().addAll(TPAFenvironment.BLUEFONT, TPAFenvironment.SMALLFONT);
	        all.setOnAction(listener);
	        
	        ruleItems.getChildren().add(all);
	        tp.setContent(ruleItems);
	        
	        HashMap<String, String> rules = files.get(key);
	        SortedSet<String> rulesNames = new TreeSet<String>(rules.keySet());
			for (String rulesName : rulesNames) {	        	
	        	String name = rulesName;
	        	name = name.replace("_", " ");
	        	
	        	CheckBox checker = new CheckBox(name);
	        	checker.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
	        	checker.setTooltip(new Tooltip(rules.get(rulesName)));
	        	checker.setOnAction(listener);
	        	
	    	    ruleItems.getChildren().addAll(checker);
	    	    
	        }
	        accordion.getPanes().addAll(tp);
	    }
	    
		StackPane resetStack = new StackPane();
		resetStack.setAlignment(Pos.CENTER_RIGHT);
		
		Text reset = new Text("Reset DRT");
		reset.setId("reset");
		reset.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
		reset.setOnMouseClicked(listener);
		resetStack.getChildren().add(reset);
		
		position.setTop(resetStack);
		position.setCenter(accordion);
		
	}

	
}

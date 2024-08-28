package com.ericsson.procus.tpaf.view.elements.options;

import java.util.ArrayList;
import java.util.HashMap;

import com.ericsson.procus.tpaf.controller.TpViewController;
import com.ericsson.procus.tpaf.model.ModelManager;
import com.ericsson.procus.tpaf.utils.CssHandler;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;

import javafx.collections.ObservableList;
import javafx.scene.Node;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Dialogs;
import javafx.scene.control.Label;
import javafx.scene.control.RadioButton;
import javafx.scene.control.Separator;
import javafx.scene.control.TextField;
import javafx.scene.control.Dialogs.DialogOptions;
import javafx.scene.control.Dialogs.DialogResponse;
import javafx.scene.control.ToggleGroup;
import javafx.scene.layout.ColumnConstraints;
import javafx.scene.layout.ColumnConstraintsBuilder;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.util.Callback;

public class TpCreateOptions {
	
	public static String[] tpOptions = {"Create_Tech_Pack", "Activate_Tech_Pack", "Generate_Tech_Pack_Sets", "Create_Tech_Pack_tpi_file", "Encrypt_Tech_Pack_tpi"};
	public static String[] IntfOptions = {"Create_Interfaces", "Activate_Interfaces", "Generate_Interface_Sets", "Create_Interface_tpi_files", "Encrypt_Interface_tpis"};
	public static String[] docOptions = {"Create_Tech_Pack_Description_Doc", "Create_XLS_doc", "Create_Universe_Description_Doc","Create_XML_doc"};
	public static String[] BOOptions = {"Create_Verification_Reports", "Create_Package", "Encrypt_Package"};
	private View view; 
	private TpViewController listener;
	
	private TextField location, ODBC, BISIP, UserName, Password;
	private CheckBox BOEncrypt;
	private VBox tpCreateBase, IntfCreateBase, BoCreateBase;
	private HBox docCreateBase, BOOptionsBase;
	private ToggleGroup radioGroup, BOVersionGroup;
	
	private HashMap<String, Object> results = new HashMap<String, Object>();
	
	public TpCreateOptions(View view, TpViewController listener){
		this.view = view;
		this.listener = listener;
	}
	
	public HashMap<String, Object> showOptionsWindow(){
		VBox base = new VBox();
		base.setSpacing(20);
		
		CssHandler css = new CssHandler();
		base.getStylesheets().add(css.getCssFileName());
		
		GridPane grid = new GridPane();
		grid.setHgap(10);
		grid.setVgap(10);
		
		location = new TextField();
		location.setPrefColumnCount(20);
		location.setPromptText("<ServerName>.athtem.eei.ericsson.se");
		
		grid.add(new Label("Server Name:"), 0, 0);
		grid.add(location, 1, 0);
		
		GridPane createOptions = new GridPane();
		createOptions.setVgap(10);
		createOptions.setHgap(10);
		ColumnConstraints widthconstraint = ColumnConstraintsBuilder.create().percentWidth(50).build();
		createOptions.getColumnConstraints().addAll(widthconstraint, widthconstraint);
		
		tpCreateBase = new VBox();
		tpCreateBase.setSpacing(5);
		tpCreateBase.getChildren().addAll(new Label("Tech Pack Options"), new Separator());
		for(String option : tpOptions){
			CheckBox checker = new CheckBox(option.replace("_", " "));
			checker.setId(option);
        	checker.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
        	checker.setOnAction(listener);
        	tpCreateBase.getChildren().addAll(checker);
		}
		
		IntfCreateBase = new VBox();
		IntfCreateBase.setSpacing(5);
		IntfCreateBase.getChildren().addAll(new Label("Interface Options"), new Separator());
		for(String option : IntfOptions){
			CheckBox checker = new CheckBox(option.replace("_", " "));
			checker.setId(option);
        	checker.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
        	checker.setOnAction(listener);
        	IntfCreateBase.getChildren().addAll(checker);
		}
		createOptions.getChildren().addAll(tpCreateBase, IntfCreateBase);
		GridPane.setConstraints(tpCreateBase, 0, 0);
	    GridPane.setConstraints(IntfCreateBase, 1, 0);	    
	    
	    BoCreateBase = new VBox();
	    BoCreateBase.setSpacing(5);
	    BoCreateBase.getChildren().addAll(new Label("BO Options"), new Separator());
	    
	    BOVersionGroup = new ToggleGroup();
	    HBox BOVersionBase = new HBox();
	    BOVersionBase.setSpacing(10);
	    RadioButton BI3 = new RadioButton("Use BI 3");
	    BI3.setId("BI_3");
	    BI3.setToggleGroup(BOVersionGroup);
	    BI3.setOnAction(listener);
	    RadioButton BI4 = new RadioButton("Use BI 4.1");
	    BI4.setId("BI_4");
	    BI4.setToggleGroup(BOVersionGroup);
	    BI4.setOnAction(listener);
	    BOVersionBase.getChildren().addAll(BI3, BI4);
	    
	    radioGroup = new ToggleGroup();
	    HBox radioBase = new HBox();
	    radioBase.setSpacing(5);
	    RadioButton create = new RadioButton("Create Universe");
	    create.setId("Create");
	    create.setToggleGroup(radioGroup);
	    create.setOnAction(listener);
	    RadioButton update = new RadioButton("Update Universe");
	    update.setId("Update");
	    update.setToggleGroup(radioGroup);
	    update.setOnAction(listener);
	    radioBase.getChildren().addAll(create, update);
	    
	    GridPane boGrid = new GridPane();
	    boGrid.setHgap(10);
	    boGrid.setVgap(5);	    
	    ODBC = new TextField();
	    ODBC.setPrefColumnCount(15);
	    ODBC.setPromptText("ODBC Connection Name");
		boGrid.add(new Label("ODBC Connection:"), 0, 0);
		boGrid.add(ODBC, 1, 0);
		
		BISIP = new TextField();
		BISIP.setPrefColumnCount(15);
		BISIP.setPromptText("BIS server IP address");
		boGrid.add(new Label("BIS IP:"), 0, 1);
		boGrid.add(BISIP, 1, 1);
		
		UserName = new TextField();
		UserName.setPrefColumnCount(15);
		UserName.setPromptText("Administrator");
		boGrid.add(new Label("BIS Username:"), 0, 2);
		boGrid.add(UserName, 1, 2);
		
		Password = new TextField();
		Password.setPrefColumnCount(15);
		Password.setPromptText("Password");
		boGrid.add(new Label("BIS Password:"), 0, 3);
		boGrid.add(Password, 1, 3);
		
		BOOptionsBase = new HBox();
		BOOptionsBase.setSpacing(5);
		for(String option : BOOptions){
			CheckBox checker = new CheckBox(option.replace("_", " "));
			checker.setId(option);
        	checker.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
        	BOOptionsBase.getChildren().addAll(checker);
		}
	    
		BoCreateBase.getChildren().addAll(BOVersionBase, radioBase, boGrid, BOOptionsBase);
		
		VBox docCreate = new VBox();
	    docCreate.setSpacing(5);
	    docCreate.getChildren().addAll(new Label("Documentation Options"), new Separator());
	    docCreateBase = new HBox();
	    docCreateBase.setId("docCreateBase");
	    docCreateBase.setSpacing(10);
	    
	    GridPane gird = new GridPane();
	    gird.setHgap(10);
	    gird.setVgap(5);
	    int itemCount = 0;
	    for(int i=0; i<docOptions.length; i++){
	    	CheckBox checker = new CheckBox(docOptions[i].replace("_", " "));
			checker.setId(docOptions[i]);
        	checker.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
        	if(i%2==0){
        		gird.add(checker, 0, itemCount);
        	}else{
        		gird.add(checker, 1, itemCount);
        		itemCount++;
        	}
	    }
	    docCreateBase.getChildren().addAll(gird);
		docCreate.getChildren().addAll(docCreateBase);
		
		base.getChildren().addAll(grid, createOptions, BoCreateBase, docCreate);
		
		DialogResponse resp = Dialogs.showCustomDialog(view.getStage(), base, "Please select the options", "Tech Pack Creation", 
				DialogOptions.OK_CANCEL, myCallback);
		
		if(resp == DialogResponse.CANCEL){
			results.clear();
		}
		
		return results;
	}
	
	
	Callback<Void, Void> myCallback = new Callback<Void, Void>() {
		@Override
		public Void call(Void param) {
			if(location.getText().length()>0){
				results.put("ServerName", location.getText());
			}
			
			ArrayList<String> ticked = new ArrayList<String>();
			ObservableList<Node> list = tpCreateBase.getChildren();
			for(Node node : list){
				if(node instanceof CheckBox){
					CheckBox cb = (CheckBox)node;
					if(cb.isSelected()){
						ticked.add(cb.getId());
					}
				}
			}
			
			list = IntfCreateBase.getChildren();
			for(Node node : list){
				if(node instanceof CheckBox){
					CheckBox cb = (CheckBox)node;
					if(cb.isSelected()){
						ticked.add(cb.getId());
					}
				}
			}
			
			list = docCreateBase.getChildren();
			for(Node node : list){
				if(node instanceof GridPane){
					GridPane box = (GridPane)node;
					for(Node checker : box.getChildren()){
						if(checker instanceof CheckBox){
							CheckBox cb = (CheckBox)checker;
							if(cb.isSelected()){
								if(!cb.getId().equals("Create_Universe_Description_Doc")){
									ticked.add(cb.getId());
								}else{
									results.put("UniDoc", "true");
								}
							}
						}
					}
				}
				
				if(node instanceof CheckBox){
					CheckBox cb = (CheckBox)node;
					if(cb.isSelected()){
						ticked.add(cb.getId());
					}
				}
			}

			if(!ticked.isEmpty()){
				results.put("Create", ticked);
			}
			
			RadioButton button = ((RadioButton)BOVersionGroup.getSelectedToggle());
			if(button != null){
				String value = button.getId();
				results.put("BIversion", value);
				System.out.println(value);
			}

			button = ((RadioButton)radioGroup.getSelectedToggle());
			if(button != null){
				String value = button.getId();
				results.put("BOjobType", value);
				System.out.println(value);
			}
			
			String value = ODBC.getText();
			if(value.length()>0){
				results.put("ODBCname", value);
			}
			
			value = BISIP.getText();
			if(value.length()>0){
				results.put("BISip", value);
			}
			
			value = Password.getText();
			if(value.length()>0){
				results.put("Password", value);
			}
			
			value = UserName.getText();
			if(value.length()>0){
				results.put("UserName", value);
			}
			
			list = BOOptionsBase.getChildren();
			for(Node node : list){
				if(node instanceof CheckBox){
					CheckBox cb = (CheckBox)node;
					if(cb.isSelected()){
						results.put(cb.getId(), "True");
					}
				}
			}
				
			
			
			return null;
		}
	};
	
	
	
}

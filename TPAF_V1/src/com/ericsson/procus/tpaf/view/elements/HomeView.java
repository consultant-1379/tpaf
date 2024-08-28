package com.ericsson.procus.tpaf.view.elements;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.Button;
import javafx.scene.control.Separator;
import javafx.scene.control.Tab;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
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
import com.ericsson.procus.tpaf.model.ModelManager;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;

public class HomeView {
	
	private Controller listener;
	
	public void setListener(Controller listener){
		this.listener = listener;
	}

	public Tab drawHomeTab(){
		Tab tab1 = new Tab("Home");
		tab1.setClosable(false);
		
		VBox titlebase = new VBox();
		titlebase.setAlignment(Pos.TOP_LEFT);
		titlebase.setPadding(new Insets(0, 10, 0, 5));
		
		Text Title = new Text("Manage Tech Packs");
	    Title.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.XLFONT);
	    titlebase.getChildren().addAll(Title, new Separator());
		
		VBox base = new VBox();
		base.setSpacing(20);
		base.setId("HomeVBox");
		base.getStyleClass().add(TPAFenvironment.BASE_BACKGROUND);

		Text loadtitle = new Text("Load from a new input");
		loadtitle.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.LARGEFONT);
		
		GridPane optionsGrid = new GridPane();
		optionsGrid.setId("options");
		optionsGrid.setPadding(new Insets(10, 20, 10, 20));
		optionsGrid.setHgap(20);
		
		Button xml = new Button("TP AF XML file");
		xml.setWrapText(true);
	    xml.setId("xmlLoad");
	    xml.setPrefSize(500, 150);
	    xml.getStyleClass().addAll(TPAFenvironment.XMLLOAD, TPAFenvironment.LARGEFONT);
	    xml.setOnAction(listener);
		
		Button fd = new Button("Function Description");
		fd.setWrapText(true);
		fd.setId("FDload");
		fd.setPrefSize(500, 150);
		fd.getStyleClass().addAll(TPAFenvironment.FDLOAD, TPAFenvironment.LARGEFONT);
		fd.setOnAction(listener);
	    
	    Button server = new Button("Server");
	    server.setWrapText(true);
	    server.setId(TPAFenvironment.SERVERLOAD);
	    server.setPrefSize(500, 150);
	    server.getStyleClass().addAll(TPAFenvironment.SERVERLOAD, TPAFenvironment.LARGEFONT);
	    server.setOnAction(listener);
	    
	    Button tpi = new Button("Tpi file");
	    tpi.setWrapText(true);
	    tpi.setId("tpiLoad");
	    tpi.setPrefSize(500, 150);
	    tpi.getStyleClass().addAll(TPAFenvironment.TPILOAD, TPAFenvironment.LARGEFONT);
	    tpi.setOnAction(listener);
	    
	    optionsGrid.getChildren().addAll(fd, server, tpi, xml);
	    GridPane.setConstraints(xml, 0, 0);
	    GridPane.setConstraints(fd, 1, 0);
	    GridPane.setConstraints(server, 2, 0);
	    GridPane.setConstraints(tpi, 3, 0);
	    
	    ColumnConstraints widthconstraint = ColumnConstraintsBuilder.create().percentWidth(25).build();
	    optionsGrid.getColumnConstraints().addAll(widthconstraint, widthconstraint,widthconstraint);
		
	    
	    Text manageTitle = new Text("Loaded Tech Packs");
	    manageTitle.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.LARGEFONT);
	    
	    
		StackPane tableview = new StackPane();
	    TableView<ModelInterface> table = new TableView<ModelInterface>();
	    table.setId("LoadedTable");
	    table.setEditable(false);
	    
	    TableColumn<ModelInterface, String> TPNameCol = new TableColumn<ModelInterface, String>("Tech Pack Name");
        TPNameCol.setCellValueFactory(new PropertyValueFactory<ModelInterface, String>("TechPackName"));
        
        TableColumn<ModelInterface, String> TPrStateCol = new TableColumn<ModelInterface, String>("R-State");
        TPrStateCol.setCellValueFactory(new PropertyValueFactory<ModelInterface, String>("Rstate"));
 
        TableColumn<ModelInterface, String> ProdNumCol = new TableColumn<ModelInterface, String>("Prod. Number");
        ProdNumCol.setCellValueFactory(new PropertyValueFactory<ModelInterface, String>("ProductNumber"));
 
        TableColumn<ModelInterface, String> ENIQversionCol = new TableColumn<ModelInterface, String>("ENIQ Version");
        ENIQversionCol.setCellValueFactory(new PropertyValueFactory<ModelInterface, String>("EniqVersion"));
        
        TableColumn<ModelInterface, String> SourceCol = new TableColumn<ModelInterface, String>("Load Source");
        SourceCol.setCellValueFactory(new PropertyValueFactory<ModelInterface, String>("LoadSource"));
        
        TableColumn<ModelInterface, String> LoadDateCol = new TableColumn<ModelInterface, String>("Load Date");
        LoadDateCol.setCellValueFactory(new PropertyValueFactory<ModelInterface, String>("LoadDate"));
	    
		
        table.setItems(ModelManager.getInstance().data);
        
        table.getColumns().addAll(TPNameCol, TPrStateCol, ProdNumCol, ENIQversionCol, SourceCol, LoadDateCol);
        table.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY);
        
        tableview.getChildren().add(table);
        tableview.setPadding(new Insets(10, 100, 10, 100));
		
        
        HBox options = new HBox();
        options.setSpacing(20);
        options.setAlignment(Pos.CENTER);
        
        Button view = new Button("View");
        view.setWrapText(true);
        view.setId("view");
        view.setPrefSize(100, 30);
        view.getStyleClass().addAll(TPAFenvironment.BUTTONSTYLE);
        view.setOnAction(listener);
	    
	    Button remove = new Button("Remove");
	    remove.setWrapText(true);
	    remove.setId("remove");
	    remove.setPrefSize(100, 30);
	    remove.getStyleClass().addAll(TPAFenvironment.BUTTONSTYLE);
	    remove.setOnAction(listener);
        
	    options.getChildren().addAll(view, remove);
	    
        
	    base.getChildren().addAll(titlebase,loadtitle, optionsGrid, manageTitle, tableview, options);
	    base.setAlignment(Pos.TOP_CENTER);
	    

	    tab1.setContent(base);
		
		return tab1;
	}
	
	
}

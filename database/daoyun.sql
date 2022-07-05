/*==============================================================*/
/* DBMS name:      MySQL 8.0.19                                 */
/* Created on:     2021/4/4 19:12:01                           */
/*==============================================================*/


drop table if exists Course;

drop table if exists Course_Sign;

drop table if exists Course_Student;

drop table if exists Dictionary;

drop table if exists DictionaryDetail;

drop table if exists Menu;

drop table if exists Permision;

drop table if exists Role;

drop table if exists RoleDescription;

drop table if exists TeacherSign;

drop table if exists User;

drop table if exists User_Role;

/*==============================================================*/
/* Table: Course                                                */
/*==============================================================*/
create table Course
(
   CourseId             int not null auto_increment,
   CourseName           varchar(255),
   CourseHour           int,
   TeachId              int not null,
   CoursePlace          varchar(255),
   primary key (CourseId)
);

/*==============================================================*/
/* Table: Course_Sign                                           */
/*==============================================================*/
create table Course_Sign
(
   SignId               int not null auto_increment,
   CourseId             int,
   StudentId            int,
   SignPlace            varchar(255),
   SignTime             datetime,
   SignStatus           int,
   primary key (SignId)
);

/*==============================================================*/
/* Table: Course_Student                                        */
/*==============================================================*/
create table Course_Student
(
   Id                   int not null auto_increment,
   CourseId             int,
   StudentId            int,
   StudentEXP           int,
   primary key (Id)
);

/*==============================================================*/
/* Table: Dictionary                                            */
/*==============================================================*/
create table Dictionary
(
   DicId                int not null,
   DicName              varchar(255),
   DicDescription       varchar(255),
   Code                 varchar(255),
   primary key (DicId)
);

/*==============================================================*/
/* Table: DictionaryDetail                                      */
/*==============================================================*/
create table DictionaryDetail
(
   Id                   int not null auto_increment,
   DicId                int,
   ItemKey              int,
   ItemValue            varchar(32),
   IsDefault            int,
   Code                 varchar(255),
   primary key (Id)
);

/*==============================================================*/
/* Table: Menu                                                  */
/*==============================================================*/
create table Menu
(
   MenuId               int not null auto_increment,
   MenuName             varchar(255),
   MenuURL              varchar(255),
   MenuIcon             varchar(32),
   primary key (MenuId)
);

/*==============================================================*/
/* Table: Permision                                             */
/*==============================================================*/
create table Permision
(
   PermissionId         int not null auto_increment,
   MenuId               int,
   PermissionName       varchar(255),
   PermissionDescription varchar(255),
   ParentId             int,
   primary key (PermissionId)
);

/*==============================================================*/
/* Table: Role                                                  */
/*==============================================================*/
create table Role
(
   RoleId               int not null auto_increment,
   RoleName             varchar(255),
   RoleDescription      varchar(255),
   IsLock               int,
   Creator              varchar(20),
   CreationDate         datetime,
   primary key (RoleId)
);

/*==============================================================*/
/* Table: RoleDescription                                       */
/*==============================================================*/
create table RoleDescription
(
   RolePermisionId      int not null auto_increment,
   RoleId               int,
   RightId              int,
   primary key (RolePermisionId)
);

/*==============================================================*/
/* Table: TeacherSign                                           */
/*==============================================================*/
create table TeacherSign
(
   TeacherSignId        int not null auto_increment,
   TeacherId            int,
   CourseId             int,
   Date                 datetime,
   primary key (TeacherSignId)
);

/*==============================================================*/
/* Table: User                                                  */
/*==============================================================*/
create table User
(
   UserId               int not null auto_increment,
   UserName             varchar(255),
   UserEducation        varchar(255),
   PhoneNumber          varchar(255),
   Password             varchar(255),
   School               varchar(255),
   Academy              varchar(255),
   Major                varchar(255),
   primary key (UserId)
);

/*==============================================================*/
/* Table: User_Role                                             */
/*==============================================================*/
create table User_Role
(
   Id                   int not null auto_increment,
   UserId               int,
   RoleId               int,
   primary key (Id)
);

alter table Course add constraint FK_Reference_4 foreign key (TeachId)
      references User (UserId);

alter table Course_Sign add constraint FK_Reference_5 foreign key (CourseId)
      references Course (CourseId) on delete restrict on update restrict;

alter table Course_Sign add constraint FK_Reference_6 foreign key (StudentId)
      references User (UserId) on delete restrict on update restrict;

alter table Course_Student add constraint FK_Reference_2 foreign key (CourseId)
      references Course (CourseId) on delete restrict on update restrict;

alter table Course_Student add constraint FK_Reference_3 foreign key (StudentId)
      references User (UserId) on delete restrict on update restrict;

alter table DictionaryDetail add constraint FK_Reference_7 foreign key (DicId)
      references Dictionary (DicId) on delete restrict on update restrict;

alter table Permision add constraint FK_Reference_11 foreign key (MenuId)
      references Menu (MenuId) on delete restrict on update restrict;

alter table Permision add constraint FK_Reference_14 foreign key (ParentId)
      references Permision (PermissionId) on delete restrict on update restrict;

alter table RoleDescription add constraint FK_Reference_10 foreign key (RightId)
      references Permision (PermissionId) on delete restrict on update restrict;

alter table RoleDescription add constraint FK_Reference_9 foreign key (RoleId)
      references Role (RoleId) on delete restrict on update restrict;

alter table TeacherSign add constraint FK_Reference_15 foreign key (TeacherId)
      references User (UserId) on delete restrict on update restrict;

alter table TeacherSign add constraint FK_Reference_16 foreign key (CourseId)
      references Course (CourseId) on delete restrict on update restrict;

alter table User_Role add constraint FK_Reference_12 foreign key (RoleId)
      references Role (RoleId) on delete restrict on update restrict;

alter table User_Role add constraint FK_Reference_13 foreign key (UserId)
      references User (UserId) on delete restrict on update restrict;
